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


class Grass:
    def __init__(self, userid, proxy):
        self.userid = userid
        self.proxy = proxy
        self.ses = aiohttp.ClientSession()

    def log(self, msg):
        now = datetime.now(tz=timezone.utc).isoformat(" ").split(".")[0]
        print(f"{black}[{now}] {reset}{msg}{reset}")

    @staticmethod
    async def ipinfo(proxy=None):
        async with aiohttp.ClientSession() as client:
            result = await client.get("http://api.ipify.cn/", proxy=proxy)
            return await result.text()

    async def start(self):
        max_retry = 10
        retry = 1
        proxy = self.proxy
        if proxy is None:
            proxy = await Grass.ipinfo()
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
        while True:
            try:
                if retry >= max_retry:
                    self.log(f"{yellow}达到最大重试次数，跳过此代理！")
                    await self.ses.close()
                    return
                    
                async with self.ses.ws_connect(
                    "wss://proxy2.wynd.network:4444/",
                    headers=headers,
                    proxy=self.proxy,
                    timeout=1000,
                    autoclose=False,
                ) as wss:
                    # 检查连接状态
                    if wss.closed:
                        self.log(f"{red}WebSocket连接已关闭")
                        continue
                        
                    res = await wss.receive_json()
                    auth_id = res.get("id")
                    if auth_id is None:
                        self.log(f"{red}auth id 为空")
                        continue
                        
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
                    retry = 1
                    
                    while not wss.closed:  # 添加连接状态检查
                        try:
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
                            
                            await countdown(120)
                        except Exception as e:
                            self.log(f"{red}ping/pong错误: {white}{str(e)}")
                            break  # 发生错误时退出内部循环
                            
            except KeyboardInterrupt:
                await self.ses.close()
                exit()
            except Exception as e:
                self.log(f"{red}连接错误: {white}{str(e)}")
                retry += 1
                await asyncio.sleep(1)  # 添加重试延迟
                continue


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
