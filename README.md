# Grass2.0！由推特用户雪糕战神@Hy78516012开源！无任何收费！
# 2.0是第二季的意思不是2倍哈兄弟们别误解了

# 注册

没有注册的可以支持一下我，走我的邀请链接谢谢：[点击这里](https://app.getgrass.io/register/?referralCode=W2P80MXsTm9LaC6)

# 警告和注意事项

所有女巫风险由用户自行承担！

本程序仅支持一个账户可多IP

# 关于代理
不做任何代理推荐！！！
本脚本仅供学习参考！！！
一切行为与我无关
使用的格式如下例所示：
示例格式：
```
http://host:port
socks5://host:port
http://user:password@host:port
socks5://user:password@host:port
```

# 使用方法

1. 确保你的设备已经安装了 Python 和 Git
   
2. 在设备上打开终端（CMD/Powershell/Terminal）

3. 克隆此仓库。你可以使用以下命令：
   ```shell
   git clone https://github.com/GzGod/Grass2.0
   如果这个方式不行那就直接把这个库保存为压缩包 右上角code里可以看到
   然后解压之后把路径复制到powershell里输入"cd 你的路径"
   ```

4. 进入 grass 文件夹：
   ```shell
   cd Grass2.0
   ```

5. 然后安装所需的库：
   ```shell
   python -m pip install -r requirements.txt
   ```

6. 根据我在 [关于代理](#关于代理) 中提供的示例，在 proxies.txt 文件中填写你的代理。如果你没有填写 `proxies.txt` 文件，它将自动使用你的公共 IP。

7. 先运行 `setup.py` 文件。你将被提示输入你的 Grass 账户邮箱和密码以获取认证（ID 和 token）。如果遇到任何错误或其他问题，请手动获取你的 userid 和 token。参见 [获取数据的 JavaScript 代码](#获取数据的-javascript-代码)
注意 这一步如果提示：ModuleNotFoundError: No module named 'httpx' 请安装httpx库：输入 pip install httpx
实在不会就把报错信息复制到GPT去问

9. 运行 `main.py` 文件

# 获取数据的 JavaScript 代码

## 获取用户 ID 的代码

确保你已经登录到 Grass 网站。

你可以在浏览器的开发工具/开发选项的控制台菜单中粘贴以下 JavaScript 代码。

获取用户 ID 的 JavaScript 代码如下：
```javascript
copy(JSON.parse(localStorage.getItem("userId")))
```

上述代码会自动将用户 ID 复制到你的剪贴板，所以你只需将其粘贴到 `userid.txt` 文件中。

## 获取 token 的代码

获取 token 的 JavaScript 代码如下：
```javascript
copy(JSON.parse(localStorage.getItem("accessToken")))
```

上述代码会自动将 token 复制到你的剪贴板，所以你只需将其粘贴到 `token.txt` 文件中。

# 支持

本人致力于无偿开源一些脚本，如果你支持我的话可以给我一些打赏：
EVM地址：`0x9f2a573c1396f2eccd19c96a75a8e9e85c2f7a62`

# 感谢
