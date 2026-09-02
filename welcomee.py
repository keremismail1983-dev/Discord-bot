import discord
from discord.ext import commands
import json
import os

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


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
    except:
        return {}


def save_languages():
    with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            user_languages,
            f,
            ensure_ascii=False,
            indent=4
        )


user_languages = load_languages()


# =========================
# LANGUAGES
# =========================

LANGUAGES = {

    "tr": {
        "rules_link_msg":
            "🇹🇷 Diliniz Türkçe olarak seçildi! "
            "Lütfen devam etmek için <#KURALLAR_KANAL_ID> "
            "kanalındaki kuralları okuyun ve aşağıdaki butona tıklayın.",

        "accept_btn":
            "Kuralları Kabul Et ve İçeri Gir",

        "success":
            "Başarıyla doğrulandın, kanalların kilidi açıldı!",

        "already_verified":
            "Zaten doğrulanmışsın!",

        "lang_changed":
            "Diliniz Türkçe olarak güncellendi "
            "(Tekrar kural okumanız gerekmez).",

        "ticket_welcome":
            "🎫 **Destek Talebi**\n\n"
            "Hoş geldin {mention}! "
            "Destek ekibi en kısa sürede seninle ilgilenecektir.\n\n"
            "Lütfen problemini veya talebini buraya yaz.",

        "ticket_btn":
            "Bilet Kapat",

        "panel_title":
            "🎫 Destek Paneli",

        "panel_desc":
            "Destek talebi açmak için aşağıdaki butona tıkla.",

        "create_btn":
            "Destek Talebi Aç",

        "no_lang":
            "⚠️ Lütfen önce `#language` kanalından dilinizi seçin!",

        "ticket_created":
            "Ticket oluşturuldu: {channel}",

        "closed":
            "Ticket kapatılıyor..."
    },


    "en": {
        "rules_link_msg":
            "🇬🇧 Language set to English! "
            "Please read the rules in <#KURALLAR_KANAL_ID> "
            "and click the button below.",

        "accept_btn":
            "Accept Rules & Enter",

        "success":
            "Successfully verified, channels unlocked!",

        "already_verified":
            "You are already verified!",

        "lang_changed":
            "Language updated to English "
            "(No need to read the rules again).",

        "ticket_welcome":
            "🎫 **Support Ticket**\n\n"
            "Welcome {mention}! "
            "Support staff will be with you shortly.\n\n"
            "Please describe your problem or request here.",

        "ticket_btn":
            "Close Ticket",

        "panel_title":
            "🎫 Support Panel",

        "panel_desc":
            "Click the button below to open a support ticket.",

        "create_btn":
            "Create Ticket",

        "no_lang":
            "⚠️ Please select your language in `#language` first!",

        "ticket_created":
            "Ticket created: {channel}",

        "closed":
            "Ticket is being closed..."
    },


    "jp": {
        "rules_link_msg":
            "🇯🇵 言語が日本語に設定されました！"
            "<#KURALLAR_KANAL_ID> チャンネルで規約を確認し、"
            "下のボタンを押してください。",

        "accept_btn":
            "規約に同意して入室する",

        "success":
            "認証が完了しました。チャンネルのロックが解除されました！",

        "already_verified":
            "すでに認証されています！",

        "lang_changed":
            "言語が日本語に更新されました。"
            "（規約の再確認は必要ありません）",

        "ticket_welcome":
            "🎫 **サポートチケット**\n\n"
            "ようこそ {mention}さん！"
            "スタッフがまもなく対応いたします。\n\n"
            "問題やお問い合わせ内容をこちらに入力してください。",

        "ticket_btn":
            "チケットを閉じる",

        "panel_title":
            "🎫 サポートパネル",

        "panel_desc":
            "下のボタンをクリックしてサポートチケットを開いてください。",

        "create_btn":
            "チケットを作成",

        "no_lang":
            "⚠️ まず `#language` チャンネルで言語を選択してください！",

        "ticket_created":
            "チケットを作成しました: {channel}",

        "closed":
            "チケットを閉じています..."
    }
}


# =========================
# TICKET CLOSE BUTTON
# =========================

class TicketCloseButton(discord.ui.View):

    def __init__(self, lang="tr"):
        super().__init__(timeout=None)

        self.lang = lang

        # Butonun ID'sini dile göre farklı yapıyoruz.
        self.custom_id = f"close_ticket_{lang}"

        self.button = discord.ui.Button(
            label=LANGUAGES[lang]["ticket_btn"],
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id=f"close_ticket_{lang}"
        )

        self.button.callback = self.close_ticket
        self.add_item(self.button)

    async def close_ticket(self, interaction: discord.Interaction):

        t = LANGUAGES[self.lang]

        # Sadece staff kapatabilsin istiyorsan
        # burada permission kontrolü ekleyebiliriz.

        await interaction.response.send_message(
            t["closed"],
            ephemeral=True
        )

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
        custom_id="clean_ticket_create"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        member = interaction.user

        # Kullanıcının dili seçilmiş mi?
        lang = user_languages.get(str(member.id))

        if lang is None:

            await interaction.response.send_message(
                "⚠️ Önce `#language` kanalından dilinizi seçin!\n"
                "⚠️ Please select your language first!\n"
                "⚠️ まず `#language` チャンネルで言語を選択してください！",
                ephemeral=True
            )

            return

        t = LANGUAGES[lang]
        guild = interaction.guild

        # Aynı kişinin zaten ticketı var mı?
        existing_channel = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{member.id}"
        )

        if existing_channel:

            await interaction.response.send_message(
                t["ticket_created"].format(
                    channel=existing_channel.mention
                ),
                ephemeral=True
            )

            return

        # Ticket izinleri
        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    read_messages=False
                ),

            member:
                discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )
        }

        # Ticket oluştur
        channel = await guild.create_text_channel(
            f"ticket-{member.id}",
            overwrites=overwrites
        )

        # Ticket mesajı
        await channel.send(
            t["ticket_welcome"].format(
                mention=member.mention
            ),
            view=TicketCloseButton(lang)
        )

        # Kullanıcıya ticket linki
        await interaction.response.send_message(
            t["ticket_created"].format(
                channel=channel.mention
            ),
            ephemeral=True
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
            custom_id=f"accept_rules_{lang}"
        )

        self.button.callback = self.accept_rules
        self.add_item(self.button)

    async def accept_rules(
        self,
        interaction: discord.Interaction
    ):

        t = LANGUAGES[self.lang]

        role = discord.utils.get(
            interaction.guild.roles,
            name="member"
        )

        if role:

            if role in interaction.user.roles:

                await interaction.response.send_message(
                    t["already_verified"],
                    ephemeral=True
                )

            else:

                await interaction.user.add_roles(role)

                await interaction.response.send_message(
                    t["success"],
                    ephemeral=True
                )

        else:

            await interaction.response.send_message(
                "Hata: `member` rolü bulunamadı!",
                ephemeral=True
            )


# =========================
# LANGUAGE SELECT
# =========================

class LanguageSelectView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def process_language(
        self,
        interaction: discord.Interaction,
        lang: str
    ):

        user_id = str(interaction.user.id)

        role = discord.utils.get(
            interaction.guild.roles,
            name="member"
        )

        is_verified = (
            role is not None
            and role in interaction.user.roles
        )

        # Dili kaydet
        user_languages[user_id] = lang
        save_languages()

        t = LANGUAGES[lang]

        if is_verified:

            await interaction.response.send_message(
                t["lang_changed"],
                ephemeral=True
            )

        else:

            view = RuleAcceptView(lang)

            await interaction.response.send_message(
                t["rules_link_msg"],
                view=view,
                ephemeral=True
            )


    @discord.ui.button(
        label="Türkçe",
        style=discord.ButtonStyle.primary,
        emoji="🇹🇷",
        custom_id="select_lang_tr"
    )
    async def set_tr(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.process_language(
            interaction,
            "tr"
        )


    @discord.ui.button(
        label="English",
        style=discord.ButtonStyle.primary,
        emoji="🇬🇧",
        custom_id="select_lang_en"
    )
    async def set_en(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.process_language(
            interaction,
            "en"
        )


    @discord.ui.button(
        label="日本語",
        style=discord.ButtonStyle.primary,
        emoji="🇯🇵",
        custom_id="select_lang_jp"
    )
    async def set_jp(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.process_language(
            interaction,
            "jp"
        )


# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():

    bot.add_view(
        LanguageSelectView()
    )

    bot.add_view(
        SingleTicketPanel()
    )

    bot.add_view(
        TicketCloseButton("tr")
    )

    bot.add_view(
        TicketCloseButton("en")
    )

    bot.add_view(
        TicketCloseButton("jp")
    )

    print(f"Bot aktif: {bot.user}")


# =========================
# LANGUAGE SETUP
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_language(ctx):

    view = LanguageSelectView()

    await ctx.send(
        "🇹🇷 **Lütfen dilinizi seçin:**\n"
        "🇬🇧 **Please select your language:**\n"
        "🇯🇵 **言語を選択してください：**",
        view=view
    )


# =========================
# TICKET PANEL
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):

    view = SingleTicketPanel()

    await ctx.send(
        "**🎫 Destek / Support / サポート**\n"
        "Destek talebi açmak için aşağıdaki butona tıkla.\n"
        "Click the button below to create a ticket.\n"
        "下のボタンをクリックしてチケットを作成してください。",
        view=view
    )


# =========================
# BOT TOKEN
# =========================

bot.run(os.getenv("DISCORD_TOKEN"))

