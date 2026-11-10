
import discord
from discord import app_commands

# =================================
# VC UDID VERIFY - CONFIG
# =================================

APPLICATION_ID = "1569717539083255938"
TOKEN = input("MTU2OTcxNzUzOTA4MzI1NTkzOA.GEJFKh.gkyaThtGqyXArg0dZRpDwTnFnOTkUOy5ktoTU8 ").strip()

UDID_URL = "https://udid.tech"
verified_users = set()


# =================================
# UDID VERIFY MENU
# =================================

class UDIDView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(discord.ui.Button(
            label="LAY UDID",
            style=discord.ButtonStyle.link,
            url=UDID_URL
        ))

    @discord.ui.button(
        label="DA XAC MINH UDID",
        style=discord.ButtonStyle.success,
        custom_id="vc_verify_udid"
    )
    async def verify(self, interaction, button):

        verified_users.add(interaction.user.id)

        embed = discord.Embed(
            title="VC | XAC MINH THANH CONG",
            description=(
                "Ban da xac nhan UDID!\n\n"
                "Hay chon chuc nang ben duoi."
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            view=FunctionView(),
            ephemeral=True
        )


# =================================
# FUNCTION MENU
# =================================

class FunctionView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)
        self.selected = False

    async def interaction_check(self, interaction):

        if interaction.user.id not in verified_users:
            await interaction.response.send_message(
                "Vui long xac minh UDID truoc!",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="NHAY TAM OPTIMION",
        style=discord.ButtonStyle.primary
    )
    async def choose(self, interaction, button):

        self.selected = True

        for item in self.children:
            if item.label == "XAC NHAN LUA CHON":
                item.disabled = False

        embed = discord.Embed(
            title="NHAY TAM OPTIMION",
            description=(
                "Da chon chuc nang:\n\n"
                "NHAY TAM OPTIMION\n\n"
                "Nhan XAC NHAN de hoan tat."
            ),
            color=discord.Color.blue()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="XAC NHAN LUA CHON",
        style=discord.ButtonStyle.success,
        disabled=True
    )
    async def confirm(self, interaction, button):

        if not self.selected:
            await interaction.response.send_message(
                "Ban chua chon chuc nang!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="VC | HOAN TAT",
            description=(
                "Xac nhan thanh cong!\n\n"
                "UDID: Da xac nhan thu cong\n"
                "Chuc nang: NHAY TAM OPTIMION\n"
                "Trang thai: HOAN TAT"
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )


# =================================
# DISCORD BOT
# =================================

class VCBot(discord.Client):

    def __init__(self):

        super().__init__(
            intents=discord.Intents.default(),
            application_id=int(APPLICATION_ID)
        )

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):

        await self.tree.sync()


bot = VCBot()


@bot.event
async def on_ready():

    print("==============================")
    print("VC UDID VERIFY")
    print("BOT:", bot.user)
    print("APPLICATION:", APPLICATION_ID)
    print("STATUS: ONLINE")
    print("==============================")


# =================================
# SETUP COMMAND
# =================================

@bot.tree.command(
    name="setup",
    description="Mo bang VC UDID VERIFY"
)
async def setup(interaction: discord.Interaction):

    embed = discord.Embed(
        title="VC UDID VERIFY",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            " 1: LAY UDID\n"
            "Nhan nut LAY UDID.\n\n"
            " 2: XAC MINH\n"
            "Nhan DA XAC MINH UDID.\n\n"
            " 3: CHON CHUC NANG\n"
            "NHAY TAM OPTIMION.\n\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.from_rgb(40, 150, 255)
    )

    embed.set_footer(text="VC SYSTEM | UDID VERIFY")

    await interaction.response.send_message(
        embed=embed,
        view=UDIDView()
    )


# =================================
# RUN
# =================================

if not TOKEN:
    raise SystemExit("TOKEN KHONG DUOC DE TRONG!")

bot.run(TOKEN)
