import discord
from discord import app_commands

# VC UDID VERIFY
APPLICATION_ID = 1569717539083255938
UDID_URL = "https://udid.tech"

# Xac nhan thu cong chi duoc luu trong RAM
verified_users = set()


class UDIDView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="LAY UDID",
                style=discord.ButtonStyle.link,
                url=UDID_URL,
            )
        )

    @discord.ui.button(
        label="DA XAC MINH UDID",
        style=discord.ButtonStyle.success,
        custom_id="vc_udid_verify",
    )
    async def verify(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        verified_users.add(interaction.user.id)

        embed = discord.Embed(
            title="VC | XAC NHAN UDID",
            description=(
                "Ban da tu xac nhan da lay UDID.\n\n"
                "Day la xac nhan thu cong, bot khong tu kiem tra UDID."
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(
            embed=embed,
            view=FunctionView(),
            ephemeral=True,
        )


class FunctionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.selected = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id not in verified_users:
            await interaction.response.send_message(
                "Ban can xac nhan UDID truoc.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(
        label="NHAY TAM OPTIMION",
        style=discord.ButtonStyle.primary,
    )
    async def choose(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        self.selected = True

        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.label == "XAC NHAN LUA CHON":
                item.disabled = False

        embed = discord.Embed(
            title="NHAY TAM OPTIMION",
            description=(
                "Da chon: **NHAY TAM OPTIMION**\n\n"
                "Nhan nut XAC NHAN LUA CHON de hoan tat."
            ),
            color=discord.Color.blue(),
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="XAC NHAN LUA CHON",
        style=discord.ButtonStyle.success,
        disabled=True,
    )
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        if not self.selected:
            await interaction.response.send_message(
                "Ban chua chon chuc nang.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="VC | HOAN TAT",
            description=(
                "Da xac nhan lua chon!\n\n"
                "**Chuc nang:** NHAY TAM OPTIMION\n"
                "**UDID:** Da xac nhan thu cong\n"
                "**Trang thai:** Hoan tat"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)


class VCBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents, application_id=APPLICATION_ID)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(UDIDView())
        await self.tree.sync()


bot = VCBot()


@bot.event
async def on_ready():
    print("==============================")
    print("VC UDID VERIFY - ONLINE")
    print(f"Bot: {bot.user}")
    print(f"Application ID: {APPLICATION_ID}")
    print("==============================")


@bot.tree.command(
    name="setup",
    description="Mo bang xac minh UDID VC",
)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="VC UDID VERIFY",
        description=(
            "━━━━━━━━━━━━━━━━━━\n"
            "**BUOC 1 - LAY UDID**\n"
            "Nhan nut LAY UDID de mo udid.tech.\n\n"
            "**BUOC 2 - XAC NHAN**\n"
            "Sau khi tu lay UDID, nhan DA XAC MINH UDID.\n\n"
            "**BUOC 3 - CHON CHUC NANG**\n"
            "Chon NHAY TAM OPTIMION va xac nhan.\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.from_rgb(40, 150, 255),
    )
    embed.set_footer(text="VC SYSTEM | UDID VERIFY")

    await interaction.response.send_message(embed=embed, view=UDIDView())


def main():
    token = input("MTU2OTcxNzUzOTA4MzI1NTkzOA.Gy2eTc.NlYtLobVmQjZGF4sNz3FWXzJBoxRyhf3CPaE4Y").strip()
    if not token:
        raise SystemExit("Token dang trong.")
    bot.run(token)


if __name__ == "__main__":
    main()
