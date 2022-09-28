from quart import Quart, render_template, request,redirect, session, url_for
from quart_discord import DiscordOAuth2Session
# from discord.ext import ipc

app = Quart(__name__)
app.config["SECRET_KEY"] = "testing" # change this key later
app.config["DISCORD_CLIENT_ID"] = 964368487600496680   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "5R52QNvLMrEctEp3qpY233GvDIgfB4rH"   # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
    return await render_template("index.html")

@app.route("/login")
async def login():
    return await discord.create_session()

@app.route("/callback")
async def callback():
	try:
		await discord.callback()
	except:
		return redirect(url_for("login"))

	user = await discord.fetch_user()
	return f"{user.name}#{user.discriminator}" #You should return redirect(url_for("dashboard")) here

if __name__ == "__main__":
	app.run(debug=True)
