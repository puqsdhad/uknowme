#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import asyncio
import bisect
import contextlib
import logging
import os
from datetime import datetime, timedelta
from hashlib import sha1
from io import BytesIO
from typing import ClassVar

import pyrogram
from pyrogram import raw
from pyrogram.crypto import mtproto
from pyrogram.errors import (
    FloodPremiumWait,
    AuthKeyDuplicated,
    BadMsgNotification,
    FloodWait,
    InternalServerError,
    RPCError,
    SecurityCheckMismatch,
    ServiceUnavailable,
)
from pyrogram.raw.all import layer
from pyrogram.raw.core import FutureSalts, Int, MsgContainer, TLObject

from .internals import MsgFactory, MsgId
from pyrogram.connection import Connection

log = logging.getLogger(__name__)


class Result:
    def __init__(self):
        self.value = None
        self.event = asyncio.Event()


class Session:
    START_TIMEOUT = 2
    WAIT_TIMEOUT = 15
    SLEEP_THRESHOLD = 10
    MAX_RETRIES = 10
    ACKS_THRESHOLD = 10
    PING_INTERVAL = 5
    STORED_MSG_IDS_MAX_SIZE = 1000 * 2
    RECONNECT_THRESHOLD = timedelta(seconds=10)
    UPDATE_QUEUE_SIZE = 1000
    UPDATE_CONSUMERS = 4
    MAX_START_RETRIES = 5

    TRANSPORT_ERRORS: ClassVar = {
        404: "auth key not found",
        429: "transport flood",
        444: "invalid DC",
    }

    def __init__(
        self,
        client: pyrogram.Client,
        dc_id: int,
        auth_key: bytes,
        test_mode: bool,
        is_media: bool = False,
        is_cdn: bool = False,
    ):
        self.client = client
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.test_mode = test_mode
        self.is_media = is_media
        self.is_cdn = is_cdn

        self.connection: Connection | None = None

        self.auth_key_id = sha1(auth_key).digest()[-8:]

        self.session_id = os.urandom(8)
        self.msg_factory = MsgFactory()

        self.salt = 0

        self.pending_acks = set()

        self.results = {}

        self.stored_msg_ids = []

        self.ping_task = None
        self.ping_task_event = asyncio.Event()

        self.recv_task = None

        self.restart_task = None

        self.is_started = asyncio.Event()
        self.restart_lock = asyncio.Lock()

        self.last_reconnect_attempt = None

    async def start(self):
        failures = 0
        self._starting = True
        while True:
            self.connection = self.client.connection_factory(
                dc_id=self.dc_id,
                test_mode=self.test_mode,
                ipv6=self.client.ipv6,
                proxy=self.client.proxy,
                media=self.is_media,
                protocol_factory=self.client.protocol_factory,
            )

            try:
                await self.connection.connect()

                self.recv_task = self.client.loop.create_task(self.recv_worker())

                await self.send(raw.functions.Ping(ping_id=0), timeout=self.START_TIMEOUT)

                if not self.is_cdn:
                    await self.send(
                        raw.functions.InvokeWithLayer(
                            layer=layer,
                            query=raw.functions.InitConnection(
                                api_id=await self.client.storage.api_id(),
                                app_version=self.client.app_version,
                                device_model=self.client.device_model,
                                system_version=self.client.system_version,
                                system_lang_code=self.client.lang_code,
                                lang_code=self.client.lang_code,
                                lang_pack="",
                                query=raw.functions.help.GetConfig(),
                            ),
                        ),
                        timeout=self.START_TIMEOUT,
                    )

                self.ping_task = self.client.loop.create_task(self.ping_worker())

                log.info("Session initialized: Layer %s", layer)
                log.info("Device: %s - %s", self.client.device_model, self.client.app_version)
                log.info("System: %s (%s)", self.client.system_version, self.client.lang_code)
            except AuthKeyDuplicated as e:
                await self.stop()
                self._starting = False
                raise e
            except (OSError, TimeoutError, RPCError) as e:
                failures += 1
                await self.stop()
                if failures >= self.MAX_START_RETRIES:
                    log.warning(
                        "[%s] Session failed to start %d times in a row: %s",
                        self.client.name,
                        failures,
                        str(e) or repr(e),
                    )
                    self._starting = False
                    raise e
            except Exception as e:
                await self.stop()
                self._starting = False
                raise e
            else:
                failures = 0
                break

        if not self.is_media:
            self.client.is_connected = True

        self.is_started.set()
        self._starting = False
        self._restart_fail_streak = 0
        self._transport_flood_streak = 0

        log.info("Session started")

    async def stop(self):
        self.is_started.clear()

        current = asyncio.current_task()
        task = getattr(self, "restart_task", None)
        if task is not None and task is not current and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, asyncio.TimeoutError, RuntimeError):
                await asyncio.gather(task, return_exceptions=True)
        self.restart_task = None

        self.recent_msg_ids = getattr(self, "recent_msg_ids", [])
        del self.recent_msg_ids[:]
        self.recent_msg_ids.extend(self.stored_msg_ids[-30:])
        self.stored_msg_ids.clear()
        self.pending_acks.clear()

        self.ping_task_event.set()

        if self.ping_task is not None:
            await self.ping_task

        self.ping_task_event.clear()

        if self.connection:
            await self.connection.close()

        if self.recv_task and not self.recv_task.done():
            self.recv_task.cancel()

            with contextlib.suppress(asyncio.CancelledError, asyncio.TimeoutError, RuntimeError):
                await asyncio.wait_for(self.recv_task, timeout=1.0)

            self.recv_task = None

        consumers = getattr(self, "UpdateConsumers", None)
        if consumers:
            for task in consumers:
                if not task.done():
                    task.cancel()
            with contextlib.suppress(asyncio.CancelledError, asyncio.TimeoutError, RuntimeError):
                await asyncio.gather(*consumers, return_exceptions=True)
            setattr(self, "UpdateConsumers", [])
            setattr(self, "_update_queue", None)

        if not self.is_media and callable(self.client.disconnect_handler):
            try:
                await self.client.disconnect_handler(self.client)
            except Exception as e:
                log.exception(e)

        log.info("Session stopped")

    async def restart(self):
        async with self.restart_lock:
            now = datetime.now()
            if (
                self.last_reconnect_attempt
                and now - self.last_reconnect_attempt < self.RECONNECT_THRESHOLD
            ):
                log.info("Reconnecting too frequently, sleeping for a while")
                await asyncio.sleep(5)

            self.last_reconnect_attempt = now
            await self.stop()
            await self.start()

    async def RestartWithRetry(self, max_retries: int = 3):
        streak = getattr(self, "_restart_fail_streak", 0)
        for attempt in range(1, max_retries + 1):
            try:
                await self.restart()
                if streak:
                    log.info(
                        "[%s] Session recovered after %d failed round(s)",
                        self.client.name,
                        streak,
                    )
                self._restart_fail_streak = 0
                return
            except Exception as e:
                log.warning(
                    "[%s] Reconnect attempt %d/%d failed: %s",
                    self.client.name,
                    attempt,
                    max_retries,
                    str(e) or repr(e),
                )
                if attempt < max_retries:
                    await asyncio.sleep(min(30, 2**attempt))
        self._restart_fail_streak = streak + 1
        backoff = min(300, 10 * 2 ** min(self._restart_fail_streak, 5))
        log.error(
            "[%s] Session reconnect failed after %d attempts (streak=%d); "
            "re-arming restart in %ds",
            self.client.name,
            max_retries,
            self._restart_fail_streak,
            backoff,
        )
        self.restart_task = None
        await asyncio.sleep(backoff)
        self.restart_task = self.client.loop.create_task(self.RestartWithRetry())

    def ScheduleRestart(self):
        task = getattr(self, "restart_task", None)
        if task is not None and not task.done():
            return
        self.restart_task = self.client.loop.create_task(self.RestartWithRetry())

    def GetUpdateQueue(self):
        q = getattr(self, "_update_queue", None)
        if q is None:
            if not self.is_started.is_set():
                return None

            q = asyncio.Queue(maxsize=Session.UPDATE_QUEUE_SIZE)
            setattr(self, "_update_queue", q)
            consumers = []
            for _ in range(Session.UPDATE_CONSUMERS):
                consumers.append(
                    self.client.loop.create_task(self.UpdateConsumer(q))
                )
            setattr(self, "UpdateConsumers", consumers)
        return q

    async def UpdateConsumer(self, q: asyncio.Queue):
        while True:
            body = await q.get()
            if body is None:
                q.task_done()
                break
            try:
                await self.client.handle_updates(body)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.warning(
                    "[%s] update consumer error: %s: %s",
                    getattr(self.client, "name", "?"),
                    type(e).__name__,
                    str(e)[:200],
                )
            finally:
                q.task_done()

    async def handle_packet(self, packet):
        data = await self.client.loop.run_in_executor(
            pyrogram.crypto_executor,
            mtproto.unpack,
            BytesIO(packet),
            self.session_id,
            self.auth_key,
            self.auth_key_id,
        )

        messages = data.body.messages if isinstance(data.body, MsgContainer) else [data]

        log.debug("Received: %s", data)

        for msg in messages:
            if msg.seq_no % 2 != 0:
                if msg.msg_id in self.pending_acks:
                    continue
                self.pending_acks.add(msg.msg_id)

            try:
                if len(self.stored_msg_ids) > Session.STORED_MSG_IDS_MAX_SIZE:
                    del self.stored_msg_ids[: Session.STORED_MSG_IDS_MAX_SIZE // 2]

                recent = getattr(self, "recent_msg_ids", None)

                if recent and msg.msg_id in recent:
                    recent.remove(msg.msg_id)
                    log.info(
                        "[%s] Skipping replayed packet from previous connection",
                        getattr(self.client, "name", "?"),
                    )
                    continue

                if self.stored_msg_ids:
                    if msg.msg_id < self.stored_msg_ids[0]:
                        raise SecurityCheckMismatch(
                            "The msg_id is lower than all the stored values"
                        )

                    if msg.msg_id in self.stored_msg_ids:
                        raise SecurityCheckMismatch(
                            "The msg_id is equal to any of the stored values"
                        )

                    time_diff = (msg.msg_id - MsgId()) / 2**32

                    if time_diff > 30:
                        raise SecurityCheckMismatch(
                            "The msg_id belongs to over 30 seconds in the future. "
                            "This usually means your system clock is ahead of the actual time. "
                            "Please synchronize your system time with an NTP server to avoid "
                            "this error in pyrogram."
                        )

                    if time_diff < -300:
                        raise SecurityCheckMismatch(
                            "The msg_id belongs to over 300 seconds in the past. "
                            "This usually means your system clock is behind the actual time. "
                            "Please synchronize your system time with an NTP server to avoid "
                            "this error in pyrogram."
                        )
            except SecurityCheckMismatch as e:
                log.info("Discarding packet: %s", e)
                await self.connection.close()
                return
            else:
                bisect.insort(self.stored_msg_ids, msg.msg_id)

            if isinstance(msg.body, (raw.types.MsgDetailedInfo, raw.types.MsgNewDetailedInfo)):
                self.pending_acks.add(msg.body.answer_msg_id)
                continue

            if isinstance(msg.body, raw.types.NewSessionCreated):
                continue

            msg_id = None

            if isinstance(msg.body, (raw.types.BadMsgNotification, raw.types.BadServerSalt)):
                msg_id = msg.body.bad_msg_id
            elif isinstance(msg.body, (FutureSalts, raw.types.RpcResult)):
                msg_id = msg.body.req_msg_id
            elif isinstance(msg.body, raw.types.Pong):
                msg_id = msg.body.msg_id
            elif self.client is not None and self.is_started.is_set():
                q = self.GetUpdateQueue()

                if q is not None:
                    try:
                        q.put_nowait(msg.body)
                    except asyncio.QueueFull:
                        log.warning(
                            "[%s] Update queue penuh (%d), drop update (pts self-heal)",
                            getattr(self.client, "name", "?"),
                            Session.UPDATE_QUEUE_SIZE,
                        )

            if msg_id in self.results:
                self.results[msg_id].value = getattr(msg.body, "result", msg.body)
                self.results[msg_id].event.set()

        if len(self.pending_acks) >= self.ACKS_THRESHOLD:
            log.debug("Sending %s acks", len(self.pending_acks))

            try:
                await self.send(raw.types.MsgsAck(msg_ids=list(self.pending_acks)), False)
            except OSError:
                pass
            else:
                self.pending_acks.clear()

    async def ping_worker(self):
        log.info("PingTask started")

        while True:
            try:
                await asyncio.wait_for(self.ping_task_event.wait(), self.PING_INTERVAL)
            except asyncio.TimeoutError:
                pass
            else:
                break

            with contextlib.suppress(OSError, RPCError):
                await self.send(
                    raw.functions.PingDelayDisconnect(
                        ping_id=0, disconnect_delay=self.WAIT_TIMEOUT + 10
                    ),
                    False,
                )

        log.info("PingTask stopped")

    async def recv_worker(self):
        log.info("NetworkTask started")

        while True:
            packet = await self.connection.recv()

            if packet is None or len(packet) == 4:
                if packet:
                    error_code = -Int.read(BytesIO(packet))

                    log.warning(
                        "Server sent transport error: %s (%s)",
                        error_code,
                        Session.TRANSPORT_ERRORS.get(error_code, "unknown error"),
                    )

                    if error_code in (429, 444):
                        streak = getattr(self, "_transport_flood_streak", 0)
                        delay = min(60, 5 * 2 ** min(streak, 4))
                        self._transport_flood_streak = streak + 1

                        log.error(
                            "[%s] Transport flood (%d); backing off %ds before reconnect",
                            self.client.name,
                            error_code,
                            delay,
                        )

                        await asyncio.sleep(delay)

                if self.is_started.is_set():
                    if not self.is_media:
                        self.client.is_connected = False
                    self.ScheduleRestart()
                else:
                    log.debug(
                        "[%s] Transport closed during startup; start() owns recovery",
                        getattr(self.client, "name", "?"),
                    )

                break

            self.client.loop.create_task(self.handle_packet(packet))

        log.info("NetworkTask stopped")

    async def send(
        self, data: TLObject, wait_response: bool = True, timeout: float = WAIT_TIMEOUT
    ):
        message = self.msg_factory(data)
        msg_id = message.msg_id

        if wait_response:
            self.results[msg_id] = Result()

        log.debug("Sent: %s", message)

        payload = await self.client.loop.run_in_executor(
            pyrogram.crypto_executor,
            mtproto.pack,
            message,
            self.salt,
            self.session_id,
            self.auth_key,
            self.auth_key_id,
        )

        try:
            await self.connection.send(payload)
        except OSError as e:
            self.results.pop(msg_id, None)
            raise e

        if wait_response:
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self.results[msg_id].event.wait(), timeout)

            result = self.results.pop(msg_id).value

            if result is None:
                raise TimeoutError("Request timed out")

            if isinstance(result, raw.types.RpcError):
                if isinstance(
                    data,
                    (
                        raw.functions.InvokeWithoutUpdates,
                        raw.functions.InvokeWithTakeout,
                    ),
                ):
                    data = data.query

                RPCError.raise_it(result, type(data))

            if isinstance(result, raw.types.BadMsgNotification):
                log.warning(
                    "%s: %s",
                    BadMsgNotification.__name__,
                    BadMsgNotification(result.error_code),
                )

            if isinstance(result, raw.types.BadServerSalt):
                self.salt = result.new_server_salt
                return await self.send(data, wait_response, timeout)

            return result
        return None

    async def invoke(
        self,
        query: TLObject,
        retries: int = MAX_RETRIES,
        timeout: float = WAIT_TIMEOUT,
        sleep_threshold: float = SLEEP_THRESHOLD,
    ):
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self.is_started.wait(), self.WAIT_TIMEOUT)

        if isinstance(
            query, (raw.functions.InvokeWithoutUpdates, raw.functions.InvokeWithTakeout)
        ):
            inner_query = query.query
        else:
            inner_query = query

        query_name = ".".join(inner_query.QUALNAME.split(".")[1:])
        
        while retries > 0:
            try:
                return await self.send(query, timeout=timeout)
            except (FloodWait, FloodPremiumWait) as e:
                amount = e.value

                if amount > sleep_threshold >= 0:
                    raise

                log.warning(
                    '[%s] Waiting for %s seconds before continuing (required by "%s")',
                    self.client.name,
                    amount,
                    query_name,
                )

                await asyncio.sleep(amount)
            except (OSError, InternalServerError, ServiceUnavailable) as e:
                retries -= 1
                if isinstance(e, OSError):
                    self.ScheduleRestart()
                if retries == 0:
                    raise e

                (log.warning if retries < 2 else log.info)(
                    '[%s] Retrying "%s" due to: %s',
                    Session.MAX_RETRIES - retries,
                    query_name,
                    str(e) or repr(e),
                )

                await asyncio.sleep(0.5)

        raise TimeoutError("Exceeded maximum number of retries")
