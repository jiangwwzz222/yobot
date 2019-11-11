from aiocqhttp import CQHttp

import yobot

conn = CQHttp(access_token='your-token',
              enable_http_post=False)

bot = yobot.Yobot()


@conn.on_message()
async def handle_msg(context):
    reply = bot.proc(context)
    if reply != "":
        return {'reply': reply,
                'at_sender': False}
    else:
        return None

try:
    with open as target:
        pass
except:
    port = 8080

conn.run(host='127.0.0.1', port=port)
