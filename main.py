import os
import uuid
import json
import aiohttp
import argparse
from datetime import datetime, timezone
from fake_useragent import UserAgent
from colorama import *

green = Fore.LIGHTGREEN_EX
red = Fore.LIGHTRED_EX
magenta = Fore.LIGHTMAGENTA_EX
white = Fore.LIGHTWHITE_EX
black = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
yellow = Fore.LIGHTYELLOW_EX

from aiohttp_socks import ProxyConnector


class Grass:
    def __init__(self, userid, proxy):
        self.userid = userid
        self.proxy = proxy
        self.ses = aiohttp.ClientSession(connector=self.get_connector(proxy))

    def get_connector(self, proxy):
        """
        如果提供了代理，返回一个 ProxyConnector；否则返回 None。
        """
        if proxy:
            return ProxyConnector.from_url(proxy)
        return None

    def log(self, msg):
        now = datetime.now(tz=timezone.utc).isoformat(" ").split(".")[0]
        print(f"{black}[{now}] {reset}{msg}{reset}")

    @staticmethod
    async def ipinfo(proxy=None):
        async with aiohttp.ClientSession() as client:
            result = await client.get("http://api.ipify.cn/", proxy=proxy)
            return await result.text()

    async def create_websocket_connection(self, headers):
        """创建 WebSocket 连接"""
        return await self.ses.ws_connect(
            "wss://proxy2.wynd.network:4444/",
            headers=headers,
            timeout=1000,
            autoclose=False,
        )

    async def handle_authentication(self, wss, browser_id, useragent):
        """处理认证流程"""
        res = await wss.receive_json()
        auth_id = res.get("id")
        if auth_id is None:
            self.log(f"{red}auth id 为空")
            return False

        auth_data = {
            "id": auth_id,
            "origin_action": "AUTH",
            "result": {
                "browser_id": browser_id.__str__(),
                "user_id": self.userid,
                "user_agent": useragent,
                "timestamp": int(datetime.now().timestamp()),
                "device_type": "desktop",
                "version": "4.26.2",
                "desktop_id": "lkbnfiajjmbhnfledhphioinpickokdi",
            },
        }
        await wss.send_json(auth_data)
        self.log(f"{green}成功连接 {white}到服务器!")
        return True
    async def send_heartbeat(self, wss):
        """发送心跳包"""
        ping_data = {
            "id": uuid.uuid4().__str__(),
            "version": "1.0.0",
            "action": "PING",
            "data": {},
        }
        await wss.send_json(ping_data)
        self.log(f"{white}发送 {green}ping {white}到服务器 !")

        pong_data = {"id": "F3X", "origin_action": "PONG"}
        await wss.send_json(pong_data)
        self.log(f"{white}发送 {magenta}pong {white}到服务器 !")

        await countdown(20)

    async def start(self):
        """主要运行逻辑"""

        # 初始化连接参数
        proxy = self.proxy if self.proxy else await Grass.ipinfo()
        browser_id = uuid.uuid5(uuid.NAMESPACE_URL, proxy)
        useragent = UserAgent().random
        headers = {
            "Host": "proxy2.wynd.network:4600",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": useragent,
            "Upgrade": "websocket",
            "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi",
            "Sec-WebSocket-Version": "13",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        }
        retry = 0  # 将重试计数器移到外层
        max_retry = 10

        try:
            while True:  # 外层循环处理session重建
                try:
                    while retry < max_retry:  # 内层循环处理连接重试
                        retry += 1  # 先增加重试次数

                        # 创建 WebSocket 连接
                        wss = await self.create_websocket_connection(headers)

                        if wss.closed:
                            self.log(f"{red}WebSocket连接已关闭")
                            await asyncio.sleep(20)
                            continue

                        # 处理认证
                        if not await self.handle_authentication(wss, browser_id, useragent):
                            await asyncio.sleep(20)
                            continue

                        # 重置重试计数器，因为连接成功了
                        retry = 0

                        # 保持连接活跃
                        while not wss.closed:
                            try:
                                await self.send_heartbeat(wss)
                            except Exception as e:
                                self.log(f"{red}ping/pong错误: {white}{str(e)}")
                                if not wss.closed:
                                    await wss.close()
                                break

                        self.log(f"{yellow}连接断开，等待20秒后重试...")
                        await asyncio.sleep(20)

                    # 如果达到最大重试次数，重建session
                    await self.ses.close()
                    self.ses = aiohttp.ClientSession(connector=self.get_connector(self.proxy))
                    retry = 0  # 重置重试计数器
                    self.log(f"{yellow}已重建session，重新开始连接尝试...")

                except Exception as e:
                    self.log(f"{red}连接错误: {white}{str(e)}")
                    await asyncio.sleep(20)
                    continue

        except KeyboardInterrupt:
            print('...')
            await self.ses.close()
            exit()

async def countdown(t):
    for i in range(t, 0, -1):
        minute, seconds = divmod(i, 60)
        hour, minute = divmod(minute, 60)
        seconds = str(seconds).zfill(2)
        minute = str(minute).zfill(2)
        hour = str(hour).zfill(2)
        print(f"waiting for {hour}:{minute}:{seconds} ", flush=True, end="\r")
        await asyncio.sleep(1)


async def main():
    arg = argparse.ArgumentParser()
    arg.add_argument(
        "--proxy", "-P", default="proxies.txt", help="Custom proxy input file "
    )
    args = arg.parse_args()
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"""

    {red}  本脚本由推特用户雪糕战神@Hy78516012开源使用 无任何收费！！！
    {white}Gihub    : {green}github.com/Gzgod
    {white}我的推特 ：{green}雪糕战神@Hy78516012
    {green}Get some grass !
          """
    )
    token = open("token.txt", "r").read()
    userid = open("userid.txt", "r").read()
    if len(userid) <= 0:
        print(f"{red}错误 : {white}请先输入您的用户ID!")
        exit()
    if not os.path.exists(args.proxy):
        print(f"{red}{args.proxy} 未找到，请确保 {args.proxy} 可用！")
        exit()
    proxies = open(args.proxy, "r").read().splitlines()
    if len(proxies) <= 0:
        proxies = [None]
    tasks = [Grass(userid, proxy).start() for proxy in proxies]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        import asyncio

        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
