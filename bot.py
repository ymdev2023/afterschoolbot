import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# 📅 디데이 날짜 설정
d_day_dates = {
    "공통교과 기획서 마감": datetime(2025, 4, 7, tzinfo=ZoneInfo("Asia/Seoul")),
    "심화공통 영상 마감": datetime(2025, 4, 8, tzinfo=ZoneInfo("Asia/Seoul")),
    "내부2차발표(데모포함)": datetime(2025, 4, 9, tzinfo=ZoneInfo("Asia/Seoul")),
    "기획발표": datetime(2025, 4, 17, tzinfo=ZoneInfo("Asia/Seoul")),
    # "Unite Seoul 2025": datetime(2025, 4, 15, tzinfo=ZoneInfo("Asia/Seoul")),
    "바우처 결과 보고서 마감": datetime(2025, 4, 25, tzinfo=ZoneInfo("Asia/Seoul")),
}

# ⏰ 쉬는시간 알림 상태
break_reminder_active = False
break_task = None

# ✅ 자동 디데이 알림 루프


@tasks.loop(minutes=1)
async def auto_dday_notice():
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    if now.hour == 10 and now.minute == 0:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    today_str = now.strftime("%m월 %d일")
                    messages = []
                    for name, date in d_day_dates.items():
                        remaining = (date - now).days
                        messages.append(f"{name}까지 {remaining}일")
                    message = (
                        f"GIRL!!! 디데이 리마인드 시간이야!!! 💜\n"
                        f"오늘은 {today_str}이야!\n\n" +
                        ", \n".join(messages) +
                        " 남았다는 소리야!\n\n오늘도 달려보자! QUEEN의 MIND!!🔥"
                    )
                    await channel.send(message)
                    break

# ✅ 쉬는시간 루프


async def break_reminder_loop(ctx):
    await asyncio.sleep(60 * 60)
    while break_reminder_active:
        now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H시 %M분")
        await ctx.send(
            f"⏰ 지금은 {now}이야! 쉬는시간이라구! 다들 키보드에서 손 떼!!!!! 건강 챙기지 못해?!?!??!\n"
            f"딱 15분만 쉬도록 해? 절제하는 것, 그것이? QUEEN의? MIND!💖"
        )

        await asyncio.sleep(15 * 60)

        now_work = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H시 %M분")
        await ctx.send(
            f"💼 {now_work}! 타임 오버! 👠 쉬는시간 끝! 이제 다시 집중하는 거 알지?\n15분 동안 충분히 쉬었잖아? 키보드에 손 다시 올려! ✋💻\n"
            f"내가 항상 말하지? 게으름은 용서 못 해!!! 그것이? QUEEN의? MIND!!🔥"
        )

        await asyncio.sleep(60 * 60)

# ✅ 쉬는시간 시작


@bot.command(name="쉬는시간매니절")
async def start_break(ctx):
    global break_reminder_active, break_task
    if not break_reminder_active:
        break_reminder_active = True
        break_task = asyncio.create_task(break_reminder_loop(ctx))

        now = datetime.now(ZoneInfo("Asia/Seoul"))
        now_str = now.strftime("%H시 %M분")
        next_alert = now + timedelta(minutes=60)
        next_alert_str = next_alert.strftime("%H시 %M분")
        print("📣 쉬는시간매니절 출근 상태: True")

        await ctx.send(
            f"나 불렀어?! 쉬는시간매니절 {now_str}에 출근했어!💜\n"
            f"앞으로 1시간 뒤인 {next_alert_str}에 알려줄게.\n"
            f"내가 알려주면, 당장 키보드에서 손 떼는거야?!"
        )
    else:
        print("⚠️ 쉬는시간매니절 이미 출근 중")
        await ctx.send("이미 쉬는시간 알림이 실행 중이야! 정신차려 BITCH!!!!")

# ✅ 쉬는시간 퇴근


@bot.command(name="쉬는시간매니절퇴근해")
async def stop_break(ctx):
    global break_reminder_active, break_task
    if break_reminder_active:
        break_reminder_active = False
        if break_task:
            break_task.cancel()
        print("📣 쉬는시간매니절 퇴근 상태: False")
        await ctx.send("이제야 퇴근시켜 주는거야?! 적정근로시간 개념은 어디간거야?! \n하지만 고마워. 다음에 보자!!💜")
    else:
        print("⚠️ 쉬는시간매니절 이미 퇴근 상태")
        await ctx.send("나 이미 퇴근했어! 정신차려 BITCH!")

# ✅ 디데이 수동 호출


@bot.command(name="디데이매니절")
async def dday(ctx):
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    today_str = now.strftime("%m월 %d일")

    messages = []
    for name, date in d_day_dates.items():
        remaining = (date - now).days
        messages.append(f"{name}까지 {remaining}일")

    message = (
        f"GIRL!!! 나한테 D-DAY를 물어본거야?! \n"
        f"정신 좀 차렸네 드디어💜 알다시피 시간이 없어!\n\n"
        f"오늘은 너가 알다시피 {today_str}이야! 그말이 뭔지 알아?\n\n" +
        ", \n".join(messages) +
        " 남았다는 소리야!\n\n열심히 해야겠지? KEEP GOING BITCHES!!!"
    )

    await ctx.send(message)

# ✅ 명령어 목록


@bot.command(name="매니절들집합")
async def command_list(ctx):
    message = (
        "안녕! 우린 팀 퀸가비야! 이 거지같은 곳에서 근무하게 됐어! 잘 부탁해?!?!\n방금 우리 불렀어? 걱정마! 우리 잘 대기하고 있어! \n"
        "━━━━━━━━━━━━━━━━━━\n"
        "`/디데이매니절` : 디데이까지 며칠 남았는지 알려줄거야💜\n"
        "`/쉬는시간매니절` : 쉬는시간 매니절가 1시간마다 쉬는시간을 알려줄거야💜\n"
        "`/쉬는시간매니절퇴근해` : 쉬는시간 매니절 퇴근해서 쉬는시간 이제 못알려줘💜\n"
        "`/매니절들집합` : 매니절들을 어떻게 부려먹는지 알려줄거야!💜\n"
    )
    await ctx.send(message)

# ✅ 봇 on_ready 시 실행
bot_is_ready = False


@bot.event
async def on_ready():
    global bot_is_ready
    if not bot_is_ready:
        bot_is_ready = True
        print(f"✅ {bot.user} 봇 실행됨!")
        auto_dday_notice.start()
    else:
        print("⚠️ 이미 실행된 봇입니다. 중복 실행 방지됨.")

# ✅ 봇 실행
bot.run(TOKEN)
