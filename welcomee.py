from datetime import timedelta
from flask import Flask
import discord
from discord.ext import commands
import json
import logging
import os
import threading

# =========================
# LOGGING SETUP
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DiscordBot")

# =========================
# FLASK WEB SERVER (Keep-Alive)
# =========================

app = Flask("")


@app.route("/")
def home():
  logger.info("Keep-alive ping isteği alındı.")
  return "Bot is alive and running!"


def run_web():
  app.run(host="0.0.0.0", port=8080)


def keep_alive():
  t = threading.Thread(target=run_web)
  t.start()


# =========================
# INTENTS & BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# LANGUAGE STORAGE
# =========================

LANGUAGE_FILE = "user_languages.json"


def load_languages():
  if not os.path.exists(LANGUAGE_FILE):
    return {}
  try:
    with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception as e:
    logger.error(f"Dil dosyası okunurken hata oluştu: {e}")
    return {}


def save_languages():
  try:
    with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
      json.dump(user_languages, f, ensure_ascii=False, indent=4)
  except Exception as e:
    logger.error(f"Dil dosyası kaydedilirken hata oluştu: {e}")


user_languages = load_languages()

# =========================
# LANGUAGES DICTIONARY
# =========================

LANGUAGES = {
    "tr": {
        "rules_link_msg": (
            "🇹🇷 Diliniz Türkçe olarak seçildi! Lütfen devam etmek için uygun"
            " kanaldaki kuralları okuyun ve aşağıdaki butona tıklayın."
        ),
        "accept_btn": "Kuralları Kabul Et ve İçeri Gir",
        "success": "Başarıyla doğrulandın, kanalların kilidi açıldı!",
        "already_verified": "Zaten doğrulanmışsın!",
        "lang_changed": (
            "Diliniz Türkçe olarak güncellendi (Tekrar kural okumanız gerekmez)."
        ),
        "ticket_welcome": (
            "🎫 **Destek Talebi**\n\nHoş geldin {mention}! Destek ekibi en kısa"
            " sürede seninle ilgilenecektir.\n\nLütfen problemini veya talebini"
            " buraya yaz."
        ),
        "ticket_btn": "Bilet Kapat",
        "panel_title": "🎫 Destek Paneli",
        "panel_desc": "Destek talebi açmak için aşağıdaki butona tıkla.",
        "create_btn": "Destek Talebi Aç",
        "no_lang": "⚠️ Lütfen önce dilinizi seçin!",
        "ticket_created": "Ticket oluşturuldu: {channel}",
        "closed": "Ticket kapatılıyor...",
    },
    "en": {
        "rules_link_msg": (
            "🇬🇧 Language set to English! Please read the rules and click the"
            " button below."
        ),
        "accept_btn": "Accept Rules & Enter",
        "success": "Successfully verified, channels unlocked!",
        "already_verified": "You are already verified!",
        "lang_changed": (
            "Language updated to English (No need to read the rules again)."
        ),
        "ticket_welcome": (
            "🎫 **Support Ticket**\n\nWelcome {mention}! Support staff will be"
            " with you shortly.\n\nPlease describe your problem or request here."
        ),
        "ticket_btn": "Close Ticket",
        "panel_title": "🎫 Support Panel",
        "panel_desc": "Click the button below to open a support ticket.",
        "create_btn": "Create Ticket",
        "no_lang": "⚠️ Please select your language first!",
        "ticket_created": "Ticket created: {channel}",
        "closed": "Ticket is being closed...",
    },
    "jp": {
        "rules_link_msg": (
            "🇯🇵"
            " 言語が日本語に設定されました！規約を確認し、下のボタンを押してください。"
        ),
        "accept_btn": "規約に同意して入室する",
        "success": "認証が完了しました。チャンネルのロックが解除されました！",
        "already_verified": "すでに認証されています！",
        "lang_changed": (
            "言語が日本語に更新されました。（規約の再確認は必要ありません）"
        ),
        "ticket_welcome": (
            "🎫 **サポートチケット**\n\nようこそ {mention}"
            "さん！スタッフがまもなく対応いたします。\n\n問題やお問い合わせ内容をこちらに入力してください。"
        ),
        "ticket_btn": "チケットを閉じる",
        "panel_title": "🎫 サポートパネル",
        "panel_desc": (
            "下のボタンをクリックしてサポートチケットを開いてください。"
        ),
        "create_btn": "チケットを作成",
        "no_lang": "⚠️ まず言語を選択してください！",
        "ticket_created": "チケットを作成しました: {channel}",
        "closed": "チケットを閉じています...",
    },
}

# =========================
# TICKET CLOSE BUTTON
# =========================


class TicketCloseButton(discord.ui.View):

  def __init__(self, lang="tr"):
    super().__init__(timeout=None)
    self.lang = lang
    self.custom_id = f"close_ticket_{lang}"

    self.button = discord.ui.Button(
        label=LANGUAGES[lang]["ticket_btn"],
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id=f"close_ticket_{lang}",
    )
    self.button.callback = self.close_ticket
    self.add_item(self.button)

  async def close_ticket(self, interaction: discord.Interaction):
    t = LANGUAGES[self.lang]
    logger.info(
        f"Ticket kapatılıyor: {interaction.channel.name} (Kullanıcı:"
        f" {interaction.user})"
    )
    await interaction.response.send_message(t["closed"], ephemeral=True)
    await interaction.channel.delete()


# =========================
# TICKET PANEL
# =========================


class SingleTicketPanel(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="Destek Talebi Aç / Create Ticket / チケット作成",
      style=discord.ButtonStyle.success,
      emoji="🎫",
      custom_id="clean_ticket_create",
  )
  async def create_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    member = interaction.user
    lang = user_languages.get(str(member.id))

    if lang is None:
      logger.warning(f"Dil seçmeyen kullanıcı ticket açmaya çalıştı: {member}")
      await interaction.response.send_message(
          "⚠️ Önce dilinizi seçin! / Please select your language! /"
          " まず言語を選択してください！",
          ephemeral=True,
      )
      return

    t = LANGUAGES[lang]
    guild = interaction.guild

    existing_channel = discord.utils.get(
        guild.text_channels, name=f"ticket-{member.id}"
    )

    if existing_channel:
      await interaction.response.send_message(
          t["ticket_created"].format(channel=existing_channel.mention),
          ephemeral=True,
      )
      return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(
            read_messages=True, send_messages=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True, send_messages=True
        ),
    }

    channel = await guild.create_text_channel(
        f"ticket-{member.id}", overwrites=overwrites
    )

    logger.info(f"Yeni ticket oluşturuldu: {channel.name} ({member})")

    await channel.send(
        t["ticket_welcome"].format(mention=member.mention),
        view=TicketCloseButton(lang),
    )

    await interaction.response.send_message(
        t["ticket_created"].format(channel=channel.mention), ephemeral=True
    )


# =========================
# RULE ACCEPT
# =========================


class RuleAcceptView(discord.ui.View):

  def __init__(self, lang="tr"):
    super().__init__(timeout=None)
    self.lang = lang

    self.button = discord.ui.Button(
        label=LANGUAGES[lang]["accept_btn"],
        style=discord.ButtonStyle.success,
        custom_id=f"accept_rules_{lang}",
    )
    self.button.callback = self.accept_rules
    self.add_item(self.button)

  async def accept_rules(self, interaction: discord.Interaction):
    t = LANGUAGES[self.lang]
    role = discord.utils.get(interaction.guild.roles, name="member")

    if role:
      if role in interaction.user.roles:
        await interaction.response.send_message(
            t["already_verified"], ephemeral=True
        )
      else:
        await interaction.user.add_roles(role)
        logger.info(
            "Kullanıcı kuralları kabul etti ve doğrulandı:"
            f" {interaction.user}"
        )
        await interaction.response.send_message(t["success"], ephemeral=True)
    else:
      logger.error("Hata: Sunucuda 'member' rolü bulunamadı!")
      await interaction.response.send_message(
          "Hata: `member` rolü bulunamadı!", ephemeral=True
      )


# =========================
# LANGUAGE SELECT
# =========================


class LanguageSelectView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  async def process_language(
      self, interaction: discord.Interaction, lang: str
  ):
    user_id = str(interaction.user.id)
    role = discord.utils.get(interaction.guild.roles, name="member")
    is_verified = role is not None and role in interaction.user.roles

    user_languages[user_id] = lang
    save_languages()
    logger.info(f"Kullanıcı dil seçti ({lang}): {interaction.user}")

    t = LANGUAGES[lang]

    if is_verified:
      await interaction.response.send_message(t["lang_changed"], ephemeral=True)
    else:
      view = RuleAcceptView(lang)
      await interaction.response.send_message(
          t["rules_link_msg"], view=view, ephemeral=True
      )

  @discord.ui.button(
      label="Türkçe",
      style=discord.ButtonStyle.primary,
      emoji="🇹🇷",
      custom_id="select_lang_tr",
  )
  async def set_tr(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.process_language(interaction, "tr")

  @discord.ui.button(
      label="English",
      style=discord.ButtonStyle.primary,
      emoji="🇬🇧",
      custom_id="select_lang_en",
  )
  async def set_en(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.process_language(interaction, "en")

  @discord.ui.button(
      label="日本語",
      style=discord.ButtonStyle.primary,
      emoji="🇯🇵",
      custom_id="select_lang_jp",
  )
  async def set_jp(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.process_language(interaction, "jp")


# =========================
# MODERATION & TIMEOUT UTILS
# =========================


def parse_time(time_str: str) -> int:
  """s=saniye, m=dakika, h=saat, d=gün dönüşümü"""
  if not time_str:
    return 0
  unit = time_str[-1].lower()
  val = time_str[:-1]
  if not val.isdigit():
    return 0
  val = int(val)

  if unit == "s":
    return val
  elif unit == "m":
    return val * 60
  elif unit == "h":
    return val * 3600
  elif unit == "d":
    return val * 86400
  return 0


# =========================
# BOT READY
# =========================


@bot.event
async def on_ready():
  bot.add_view(LanguageSelectView())
  bot.add_view(SingleTicketPanel())
  bot.add_view(TicketCloseButton("tr"))
  bot.add_view(TicketCloseButton("en"))
  bot.add_view(TicketCloseButton("jp"))
  logger.info(f"Bot başarıyla giriş yaptı: {bot.user}")


# =========================
# SETUP & PANEL COMMANDS
# =========================


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_language(ctx):
  view = LanguageSelectView()
  logger.info(f"Dil paneli kuruldu (Yetkili: {ctx.author})")
  await ctx.send(
      "🇹🇷 **Lütfen dilinizi seçin:**\n"
      "🇬🇧 **Please select your language:**\n"
      "🇯🇵 **言語を選択してください：**",
      view=view,
  )


@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
  view = SingleTicketPanel()
  logger.info(f"Destek paneli kuruldu (Yetkili: {ctx.author})")
  await ctx.send(
      "**🎫 Destek / Support / サポート**\n"
      "Destek talebi açmak için aşağıdaki butona tıkla.\n"
      "Click the button below to create a ticket.\n"
      "下のボタンをクリックしてチケットを作成してください。",
      view=view,
  )


# =========================
# ADVANCED MODERATION COMMANDS (with #bot-command check)
# =========================


@bot.command()
@commands.has_permissions(kick_members=True)
async def timeout(
    ctx, member: discord.Member, duration: str, *, reason="Belirtilmedi"
):
  if ctx.channel.name != "bot-command":
    await ctx.send("⚠️ Bu komut yalnızca `#bot-command` kanalında kullanılabilir!")
    return

  if member.guild.owner == member or member.guild_permissions.administrator:
    await ctx.send(
        "❌ Bu kullanıcı Sunucu Sahibi veya Yönetici olduğu için"
        " cezalandırılamaz!"
    )
    return

  seconds = parse_time(duration)
  if seconds <= 0:
    await ctx.send(
        "⚠️ Geçersiz süre formatı! Örnek kullanım: `!timeout @kullanici 1h Küfür`"
        " (s=saniye, m=dakika, h=saat, d=gün)"
    )
    return

  try:
    time_delta = timedelta(seconds=seconds)
    await member.timeout(time_delta, reason=reason)
    logger.info(
        f"[MOD] {member} kullanıcısına {duration} süreyle timeout verildi."
        f" Yetkili: {ctx.author}, Sebep: {reason}"
    )
    await ctx.send(
        f"✅ **{member}** isimli kullanıcıya **{duration}** süreyle timeout"
        f" verildi. Sebep: *{reason}*"
    )
  except Exception as e:
    logger.error(f"Timeout verme hatası: {e}")
    await ctx.send("❌ Kullanıcıya timeout verilirken bir hata oluştu.")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Belirtilmedi"):
  if ctx.channel.name != "bot-command":
    await ctx.send("⚠️ Bu komut yalnızca `#bot-command` kanalında kullanılabilir!")
    return

  if member.guild.owner == member or member.guild_permissions.administrator:
    await ctx.send(
        "❌ Bu kullanıcı Sunucu Sahibi veya Yönetici olduğu için banlanamaz!"
    )
    return

  try:
    await member.ban(reason=reason)
    logger.info(
        f"[BAN] {member} sunucudan banlandı. Yetkili: {ctx.author}, Sebep:"
        f" {reason}"
    )
    await ctx.send(f"🔨 **{member}** sunucudan banlandı. Sebep: *{reason}*")
  except Exception as e:
    logger.error(f"Banlama hatası: {e}")
    await ctx.send("❌ Kullanıcı banlanırken bir hata oluştu.")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason="Belirtilmedi"):
  if ctx.channel.name != "bot-command":
    await ctx.send("⚠️ Bu komut yalnızca `#bot-command` kanalında kullanılabilir!")
    return

  try:
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user, reason=reason)
    logger.info(
        f"[UNBAN] {user} kullanıcısının banı kaldırıldı. Yetkili: {ctx.author},"
        f" Sebep: {reason}"
    )
    await ctx.send(
        f"🔓 **{user}** isimli kullanıcının banı kaldırıldı. Sebep: *{reason}*"
    )
  except Exception as e:
    logger.error(f"Unban hatası: {e}")
    await ctx.send(
        "❌ Ban kaldırılırken bir hata oluştu. Kullanıcı ID'sini doğru"
        " girdiğinizden emin olun."
    )


# =========================
# BOT RUN WITH FLASK KEEP-ALIVE
# =========================

if __name__ == "__main__":
  logger.info("Bot ve Flask sunucusu başlatılıyor...")
  keep_alive()
  bot.run(os.getenv("DISCORD_TOKEN"))

    
