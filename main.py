import os
import uuid
import json
import aiohttp
import argparse
from datetime import datetime, timezone
from fake_useragent import UserAgent
from colorama import *
import asyncio
import ssl

# 添加代理所需的库
try:
    import aiohttp_socks
except ImportError:
    os.system('pip install aiohttp_socks')
    import aiohttp_socks

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
        self.session = None
        self.start_time = None
        self.ping_count = 0

    def log(self, msg):
        now = datetime.now(tz=timezone.utc).isoformat(" ").split(".")[0]
        print(f"{black}[{now}] {reset}{msg}{reset}")

    def get_runtime(self):
        if self.start_time:
            runtime = datetime.now() - self.start_time
            hours = runtime.seconds // 3600
            minutes = (runtime.seconds % 3600) // 60
            seconds = runtime.seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"

    async def create_session(self):
        if self.proxy and self.proxy.startswith('socks5://'):
            connector = aiohttp_socks.ProxyConnector.from_url(self.proxy)
            self.session = aiohttp.ClientSession(connector=connector)
        else:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_ip_info(self):
        try:
            if self.session is None:
                await self.create_session()
            async with self.session.get("https://api.ipify.org/", timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.log(f"{red}IP信息获取失败: HTTP {response.status}")
                    return None
        except Exception as e:
            self.log(f"{red}获取IP信息出错: {str(e)}")
            return None

    async def start(self):
        try:
            if self.session is None:
                await self.create_session()

            current_ip = await self.get_ip_info()
            if not current_ip:
                self.log(f"{red}无法获取IP信息，跳过此代理")
                await self.session.close()
                return

            self.log(f"{green}成功获取IP: {current_ip}")
            self.start_time = datetime.now()

            max_retry = 10
            retry = 1
            browser_id = str(uuid.uuid4())
            useragent = UserAgent().random
            headers = {
                "Host": "proxy2.wynd.network:4650",
                "Connection": "Upgrade",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "User-Agent": useragent,
                "Upgrade": "websocket",
                "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi",
                "Sec-WebSocket-Version": "13",
                "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            }

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            while True:
                try:
                    if retry >= max_retry:
                        self.log(f"{yellow}达到最大重试次数，跳过此代理!")
                        break

                    async with self.session.ws_connect(
                            "wss://proxy2.wynd.network:4650/",
                            headers=headers,
                            ssl=ssl_context,
                            timeout=60,
                            heartbeat=30
                    ) as ws:
                        await asyncio.sleep(2)

                        try:
                            res = await ws.receive_json(timeout=30)
                            auth_id = res.get("id")
                            if not auth_id:
                                raise ValueError("认证ID为空")

                            auth_data = {
                                "id": auth_id,
                                "origin_action": "AUTH",
                                "result": {
                                    "browser_id": browser_id,
                                    "user_id": self.userid,
                                    "user_agent": useragent,
                                    "timestamp": int(datetime.now().timestamp()),
                                    "device_type": "desktop",
                                    "version": "4.26.2",
                                    "desktop_id": "lkbnfiajjmbhnfledhphioinpickokdi",
                                },
                            }

                            await ws.send_json(auth_data)
                            self.log(f"{green}成功连接服务器 - IP: {current_ip} - 运行时间: {self.get_runtime()}")
                            retry = 1

                            while True:
                                try:
                                    ping_data = {
                                        "id": str(uuid.uuid4()),
                                        "version": "1.0.0",
                                        "action": "PING",
                                        "data": {},
                                    }
                                    await ws.send_json(ping_data)
                                    self.ping_count += 1
                                    self.log(
                                        f"{white}发送 {green}ping {white}- 计数: {self.ping_count} - 运行时间: {self.get_runtime()}")

                                    pong_data = {"id": "F3X", "origin_action": "PONG"}
                                    await ws.send_json(pong_data)
                                    self.log(f"{white}发送 {magenta}pong {white}- IP: {current_ip}")

                                    print(
                                        f"\r{green}代理状态: {current_ip} | 运行时间: {self.get_runtime()} | Ping次数: {self.ping_count}{reset}",
                                        end="")

                                    await countdown(120)

                                except Exception as e:
                                    self.log(f"{red}通信错误: {str(e)}")
                                    break

                        except Exception as e:
                            self.log(f"{red}WebSocket错误: {str(e)}")
                            retry += 1
                            continue

                except Exception as e:
                    self.log(f"{red}连接错误: {str(e)}")
                    await asyncio.sleep(5)
                    retry += 1
                    continue

        except Exception as e:
            self.log(f"{red}发生错误: {str(e)}")
        finally:
            if self.session and not self.session.closed:
                await self.session.close()


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
        "--proxy", "-P", default="proxies.txt", help="Custom proxy input file"
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
    try:
        token = open("token.txt", "r").read().strip()
    except:
        token = ""

    try:
        userid = open("userid.txt", "r").read().strip()
        if len(userid) <= 0:
            print(f"{red}错误: {white}请先输入您的用户ID!")
            exit()
    except:
        print(f"{red}错误: {white}未找到userid.txt文件!")
        exit()

    if not os.path.exists(args.proxy):
        print(f"{red}{args.proxy} 未找到，请确保 {args.proxy} 可用！")
        exit()

    proxies = []
    try:
        with open(args.proxy, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{red}读取代理文件错误: {str(e)}")
        exit()

    if len(proxies) <= 0:
        proxies = [None]

    print(f"{green}正在启动 {len(proxies)} 个代理任务...")
    print(f"{yellow}按 Ctrl+C 可以停止程序运行")

    tasks = [Grass(userid, proxy).start() for proxy in proxies]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        import asyncio

        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{red}程序被用户中断")
        exit()
    except Exception as e:
        print(f"\n{red}程序发生错误: {str(e)}")
        exit()
