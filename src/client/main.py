from aiocqhttp import CQHttp

import yobot

conn = CQHttp(access_token='your-token',
              enable_http_post=False)

bot = yobot.Yobot()


@bot.on_message()
async def handle_msg(context):
    r_list = bot.proc(context)
    if r_list != []:
        return {'reply': "\n".join(r_list),
                'at_sender': False}
    else:
        return {}

try:
    conn.run(host='127.0.0.1', port=8080)
except KeyboardInterrupt:
    del bot
    del conn
    exit()
