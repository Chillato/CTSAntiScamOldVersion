import os, json, asyncio, datetime, traceback, sqlite3
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, User
from pyrogram.errors import *
from pyrogram.session import Session
from pyrogram.types import Message

if not os.path.exists("bot_session"):
    os.mkdir("bot_session")

try:
    conn = sqlite3.connect("database.db")
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS netban (userid INT, motivo TEXT)")
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS admin (chat_id INT, ruolo TEXT)")
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS gruppi (chat_id INT)")
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS user (chat_id INT)")
    conn.commit()
except:
    traceback.print_exc()
    exit(code="Errore nel database.")

api_id = 9923700
api_hash = "c455d32dc08eae4dc7d34649a3510fc2"
bot = "5559455406:AAHfviJEf513AvX-RtWEadx2EJQJctny5fs"

client = Client("bot_session/bot", api_id, api_hash, bot_token=bot)
Session.notice_displayed = True
client.start()
print("Bot Status [ON]")

me = client.get_me()
cur = conn.cursor()
dev = [5342417758]
founder = [5342417758, 2100381021, 5339624520, 573958069]
vice = []
channel = -100
channel_arch = -1001514711143
staff_group = -1001526315165


@client.on_message(filters.command("staffnull"))
async def listastaff(_, message):
    developer = await client.get_users(5342417758)
    founder1 = await client.get_users(5339624520)
    founder2 = await client.get_users(573958069)
    founder3 = await client.get_users(2100381021)
    vicefounder = await client.get_users(5342417758)
    tex = ""
    for ad, in conn.cursor().execute("SELECT chat_id FROM admin").fetchall():
        adm = await client.get_users(ad)
        tex += f"➥ {adm.mention}\n\n"
    await message.reply_text(f"""
⚙ Lista staff di {me.mention}

👑 Owner
➥ {founder3.mention}
➥ {founder1.mention}
➥ {founder2.mention}

⚜️ Vice-Owner
➥ {vicefounder.mention}

👮‍♂️ Supporter
{tex}
""")

@client.on_message(filters.group & filters.command("netunban"))
async def netunband(_, message):
    if isAdmin(message.from_user.id):
        split = message.text.split(" ")
        if split.__len__() > 1:
            try:
                id = (await client.get_users(split[1])).id
                if checker(id):
                    mex = await message_unban(id)
                    cur.execute("DELETE FROM netban WHERE userid = ?", [id])
                    conn.commit()
                    for a, in cur.execute("SELECT chat_id FROM gruppi").fetchall():
                        try:
                            await client.unban_chat_member(a, id)
                            await client.send_message(a, mex)
                        except:
                            traceback.print_exc()
                            pass
                    await client.send_message(channel_arch, mex)
                    await message.reply_text("✅ NetUnban eseguito correttamente !")
                else:
                    await message.reply_text("❌ L'utente non è bannato !")
            except:
                traceback.print_exc()
                await message.reply_text("❌ L'utente messo non è esistente!")
        else:
            await message.reply_text("❌ Args non valide !")

@client.on_message(filters.group & filters.command("supporto"))
async def supp(_, message):
    staff = await client.get_chat_member(message.chat.id, message.from_user.id)
    if staff.privileges.can_restrict_members:
        reason = message.text.replace("/supporto", "")
        gruppo = await client.get_chat(message.chat.id)
        await message.reply_text("supporto inviato")
        await client.send_message(staff_group, f"""
🚨 Nuovo supporto di gruppo

ℹ️ Informazioni gruppo:

🙍‍♂️ Nome: {(await client.get_chat(message.chat.id)).title}
📧 Membri: {(await client.get_chat(message.chat.id)).members_count}
🆔 {(await client.get_chat(message.chat.id)).id}

📠 Motivazione
➥ {reason}

👤 Richiesta fatta da: {message.from_user.mention}
""", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Entra per dare supporto ✅", url=(await client.get_chat(message.chat.id)).invite_link)]]))


@client.on_message(filters.group & filters.command("finish"))
async def finishe(_, message):
    if isAdmin(message.from_user.id):
        await message.reply_text(f"<b>✅ Supporto finito</b>\n\n<i>{message.from_user.mention} ha finito il suo supporto fra 5 secondi verrà rimosso dal bot automaticamente</i>")
        await client.send_message(staff_group, f"<b>✅ Supporto fatto da {message.from_user.mention}</b>")
        await asyncio.sleep(5.0)
        await client.ban_chat_member(message.chat.id, message.from_user.id)
        await client.unban_chat_member(message.chat.id, message.from_user.id)

@client.on_message(filters.new_chat_members)
async def me_join(client, message):
    for user in message.new_chat_members:
        if user.is_self:
            addGroup(message.chat.id)
            await message.reply_text("""**Ciao a tutti, grazie per avermi aggiunto al tuo gruppo !**

• Non dimenticare di farmi Admin del Gruppo (sennò non potrò rimuovere gli utenti pericolosi, almeno permesso di rimuovere membri)
• Quando sono admin fai /inizia per attivare la blacklist

__Lo staff ti ringrazia per il supporto__
""")
        else:
            if checker(message.from_user.id):
                try:
                    await client.ban_chat_member(message.chat.id, message.from_user.id)
                    await message.reply_text(f"❌ {message.from_user.mention} è stato bannato perchè è presente nella blacklist !", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔰 Prove 🔰", url="t.me/CTSArchivio")]]))
                except:
                    pass

@client.on_message(filters.private)
async def cmd(client, message):
    user = message.from_user
    if message.text == "/start":
        isUserandAdd(user.id)
        await message.reply_text(await message_start(user), reply_markup=await keyboard_start())
    elif message.text != None and message.text.startswith("/sup"):
        split = message.text.split(" ")
        if split.__len__() > 1:
            try:
                split = message.text.split(" ")
                info = await client.get_users(split[1])
                if isAdmin(info.id):
                    await message.reply_text(f"✅ {info.mention} è un admin !")
                else:
                    await message.reply_text(f"❌ {info.mention} NON è un admin !")
            except:
                await message.reply_text("❌ L'utente messo non è esistente!")
        else:
            info = await client.get_users(user.id)
            if isAdmin(info.id):
                await message.reply_text(f"✅ {info.mention} è un admin !")
            else:
                await message.reply_text(f"❌ {info.mention} NON è un admin !")
    elif message.text == "/stats" and isAdmin(user.id):
        gr = cur.execute("SELECT COUNT(chat_id )FROM gruppi").fetchone()[0]
        netban = cur.execute("SELECT COUNT(userid) FROM netban").fetchone()[0]
        ut = cur.execute("SELECT COUNT(chat_id) FROM user").fetchone()[0]
        await message.reply_text(f"⚙️ Statistiche {me.mention}\n👥 Gruppi » {gr}\n🚫 NetBan » {netban}\n📋 Utenti » {ut}")
    elif message.text != None and message.text.startswith("/admin") and user.id in founder:
        try:
            split = message.text.split(" ")
            info = await client.get_users(split[1])
            if isAdmin(info.id):
                await message.reply_text(f"✅ {info.mention} è già un admin !")
            else:
                cur.execute("INSERT INTO admin (chat_id, ruolo) VALUES (?,?)", [info.id, "admin"])
                conn.commit()
                await message.reply_text(f"✅ {info.mention} reso admin !")
        except:
            await message.reply_text("❌ L'utente messo non è esistente!")
    elif message.text != None and message.text.startswith("/unadmin") and user.id in founder:
        try:
            split = message.text.split(" ")
            info = await client.get_users(split[1])
            if isAdmin(info.id):
                cur.execute("DELETE FROM admin WHERE chat_id = ?", [info.id])
                conn.commit()
                await message.reply_text(f"✅ {info.mention} tolto dal ruolo di admin !")
            else:
                await message.reply_text(f"❌ {info.mention} NON è admin !")
        except:
            await message.reply_text("❌ L'utente messo non è esistente!")
    elif message.text != None and message.text.startswith("/post") and user.id in founder:
        text = message.text.replace("/post", "")
        for a, in cur.execute("SELECT chat_id FROM user").fetchall():
            try:
                await client.send_message(a, "**⚠️ Messaggio globale da parte del founder:**\n\n"+text)
            except:
                pass
        await message.reply_text(f"**✅ ⇢ Post Inviato !**")
    elif message.text != None and message.text.startswith("/check"):
        split = message.text.split(" ")
        if split.__len__() > 1:
            try:
                split = message.text.split(" ")
                info = await client.get_users(split[1])
                if checker(info.id):
                    informazioni = get_info_netban(info.id)
                    m = informazioni["motivo"]
                    await message.reply_text(f"❌ {info.mention} è presente nella blacklist !\n\n📠 Motivazione:\n➥ {m}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔰 Prove 🔰", url="t.me/CTSArchivip")]]))
                else:
                    await message.reply_text(f"✅ {info.mention} non è presente nella blacklist !")
            except:
                await message.reply_text("❌ L'utente messo non è esistente!")
        else:
            info = await client.get_users(user.id)
            if checker(info.id):
                informazioni = get_info_netban(user.id)
                m = informazioni["motivo"]
                await message.reply_text(f"❌ {info.mention} è presente nella blacklist !\n\n📠 Motivazione:\n➥ {m}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔰 Prove 🔰", url="t.me/CTSArchivio")]]))
            else:
                await message.reply_text(f"✅ {info.mention} non è presente nella blacklist !")
    elif message.text != None and message.text.startswith("/netban"):
        if isAdmin(message.from_user.id):
            split = message.text.split(" ")
            if split.__len__() > 1:
                try:
                    id = (await client.get_users(split[1])).id
                    bv = split[1]
                    if not isAdmin(id):
                        motivo = message.text.replace(f"/netban {bv}", "")
                        mex = await message_netban(id, user.id, motivo)
                        cur.execute("INSERT INTO netban (userid, motivo) VALUES (?,?)", [id, motivo])
                        conn.commit()
                        for a, in cur.execute("SELECT chat_id FROM gruppi").fetchall():
                            try:
                                await client.ban_chat_member(a, id, disable_web_page_preview=True)
                                await client.send_message(a, mex, disable_web_page_preview=True)
                            except:
                                pass
                        await client.send_message(channel_arch, mex)
                        await message.reply_text("✅ Netban eseguito correttamente !")
                    else:
                        cur.execute("DELETE FROM netban WHERE userid = ?", [id])
                        conn.commit()
                        await message.reply_text("❌ Non puoi bannare un admin !")
                except:
                    traceback.print_exc()
                    cur.execute("DELETE FROM netban WHERE userid = ?", [id])
                    conn.commit()
                    await message.reply_text("❌ L'utente messo non è esistente!")
            else:
                cur.execute("DELETE FROM netban WHERE userid = ?", [id])
                conn.commit()
                await message.reply_text("❌ Args non valide !")
        else:
            pass
    elif message.text == "/cmd":
        if not isAdmin(user.id):
            await message.reply_text("""**🛠 Comandi**

/check [@/id] = Controlla se un utente è in BlackList [in privato e nei gruppi]
/supporter [@/id o niente] = Controlla se un utente è un supporter [in privato e nei gruppi]
""",        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙Indietro🔙", "info")]
            ]))
        else:
            await message.reply_text("""**🛠 Comandi**

👑 » Fondatore
👮‍♂️ » Amministratori
👤 » Tutti

/check [@/id] = Controlla se un utente è in BlackList [👤 in privato e nei gruppi]
/stats = Statistiche bot [👮‍♂️ 👑 in privato e nei gruppi]
/supporter [@/id o niente] = Controlla se un utente è un supporter [👤 in privato e nei gruppi]
/admin [@/id] = Aggiunge un admin [👑 in privato e nei gruppi]
/unadmin [@/id] = Toglie un admin [👑 in privato e nei gruppi]
/netban [@/id linkProve motivo] = Banna un'utente [👮‍♂️ 👑 in privato e nei gruppi]
/netunban [@/id] = Sbanna un'utente [👮‍♂️ 👑 in privato e nei gruppi]
/post [messaggio] = Post globale [👑 in privato]
/cmd = ti dice i comandi [👤]
""")
@client.on_message(filters.group)
async def cmd(client, message):
    user = message.from_user
    if message.text == "/stats" and isAdmin(user.id):
        gr = cur.execute("SELECT COUNT(chat_id )FROM gruppi").fetchone()[0]
        netban = cur.execute("SELECT COUNT(userid) FROM netban").fetchone()[0]
        ut = cur.execute("SELECT COUNT(chat_id) FROM user").fetchone()[0]
        await message.reply_text(f"⚙️ Statistiche {me.mention}\n👥 Gruppi » {gr}\n🚫 NetBan » {netban}\n📋 Utenti » {ut}")
    elif message.text != None and message.text.startswith("/sup"):
        split = message.text.split(" ")
        if split.__len__() > 1:
            try:
                split = message.text.split(" ")
                info = await client.get_users(split[1])
                if isAdmin(info.id):
                    await message.reply_text(f"✅ {info.mention} è un admin !")
                else:
                    await message.reply_text(f"❌ {info.mention} NON è un admin !")
            except:
                traceback.print_exc()
                await message.reply_text("❌ L'utente messo non è esistente!")
        else:
            info = await client.get_users(user.id)
            if isAdmin(info.id):
                await message.reply_text(f"✅ {info.mention} è un admin !")
            else:
                await message.reply_text(f"❌ {info.mention} NON è un admin !")
    elif message.text != None and message.text.startswith("/admin") and user.id in founder:
        try:
            split = message.text.split(" ")
            info = await client.get_users(split[1])
            if isAdmin(info.id):
                await message.reply_text(f"❌ {info.mention} è già un admin !")
            else:
                cur.execute("INSERT INTO admin (chat_id, ruolo) VALUES (?,?)", [info.id, "admin"])
                conn.commit()
                await message.reply_text(f"✅ {info.mention} reso admin !")
        except:
            await message.reply_text("❌ L'utente messo non è esistente!")
    elif message.text != None and message.text.startswith("/unadmin") and user.id in founder:
        try:
            split = message.text.split(" ")
            info = await client.get_users(split[1])
            if isAdmin(info.id):
                cur.execute("DELETE FROM admin WHERE chat_id = ?", [info.id])
                conn.commit()
                await message.reply_text(f"✅ {info.mention} tolto dal ruolo di admin !")
            else:
                await message.reply_text(f"❌ {info.mention} NON è admin !")
        except:
            await message.reply_text("❌ L'utente messo non è esistente!")
    elif message.text != None and message.text.startswith("/check"):
        split = message.text.split(" ")
        if split.__len__() > 1:
            try:
                split = message.text.split(" ")
                info = await client.get_users(split[1])
                if checker(info.id):
                    informazioni = get_info_netban(info.id)
                    m = informazioni["motivo"]
                    await message.reply_text(f"❌ {info.mention} è presente nella blacklist !\n\n📠 Motivazione:\n➥ {m}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔰 Prove 🔰", url="t.me/CTSArchivio")]]))
                else:
                    await message.reply_text(f"✅ {info.mention} non è presente nella blacklist !")
            except:
                await message.reply_text("❌ L'utente messo non è esistente!")
        else:
            info = await client.get_users(user.id)
            if checker(info.id):
                informazioni = get_info_netban(user.id)
                m = informazioni["motivo"]
                await message.reply_text(f"❌ {info.mention} è presente nella blacklist !\n\n📠 Motivazione:\n➥ {m}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔰 Prove 🔰", url="t.me/CTSArchivio")]]))
            else:
                await message.reply_text(f"✅ {info.mention} non è presente nella blacklist !")
    elif message.text != None and message.text.startswith("/netban"):
        if isAdmin(message.from_user.id):
            split = message.text.split(" ")
            if split.__len__() > 1:
                try:
                    id = (await client.get_users(split[1])).id
                    bv = split[1]
                    if not isAdmin(id):
                        motivo = message.text.replace(f"/netban {bv}", "")
                        mex = await message_netban(id, user.id, motivo)
                        cur.execute("INSERT INTO netban (userid, motivo) VALUES (?,?)", [id, motivo])
                        conn.commit()
                        for a, in cur.execute("SELECT chat_id FROM gruppi").fetchall():
                            try:
                                await client.ban_chat_member(a, id)
                                await client.send_message(a, mex, disable_web_page_preview=True)
                            except:
                                pass
                        await client.send_message(channel_arch, mex, disable_web_page_preview=True)
                        await message.reply_text("✅ Netban eseguito correttamente !")
                    else:
                        await message.reply_text("❌ Non puoi bannare un admin !")
                except:
                    traceback.print_exc()
                    await message.reply_text("❌ L'utente messo non è esistente!")
            else:
                cur.execute("DELETE FROM netban WHERE userid = ?", [id])
                conn.commit()
                await message.reply_text("❌ Args non valide !")
        elif message.text != None and message.text.startswith("/netunban"):
            if isAdmin(message.from_user.id):
                split = message.text.split(" ")
                if split.__len__() > 1:
                    try:
                        id = (await client.get_users(split[1])).id
                        if checker(id):
                            mex = await message_unban(id)
                            cur.execute("DELETE FROM netban WHERE userid = ?", [id])
                            conn.commit()
                            for a, in cur.execute("SELECT chat_id FROM gruppi").fetchall():
                                try:
                                    await client.unban_chat_member(a, id)
                                    await client.send_message(a, mex)
                                except:
                                    traceback.print_exc()
                                    pass
                            await client.send_message(channel_arch, mex)
                            await message.reply_text("✅ NetUnban eseguito correttamente !")
                        else:
                            await message.reply_text("❌ L'utente non è bannato !")
                    except:
                        traceback.print_exc()
                        await message.reply_text("❌ L'utente messo non è esistente!")
                else:
                    await message.reply_text("❌ Args non valide !")
    elif message.text == "/templink" and user.id in founder:
        fff = await client.create_chat_invite_link(staff_group, member_limit=1)
        FF = fff["invite_link"]
        await client.send_message(dev, f"🔗 Link:\n\n{FF}")
        await message.reply_text(f"✅ {user.mention} ti ho mandato in privato il link temporaneo del gruppo (il link non andrà più dopo che lo usa una persona)")
    elif message.text == "/inizia":
        amministratore = await client.get_chat_member(message.chat.id, message.from_user.id)
        if amministratore.privileges.can_restrict_members:
            async for member in client.get_chat_members(message.chat.id):
                if checker(member.user.id):
                    try:
                        await client.ban_chat_member(message.chat.id, member.id)
                    except:
                        pass
            await message.reply_text("✅ Blacklist attivata")
    elif message.text == "/cmd":
        if not isAdmin(user.id):
            await message.reply_text("""**🛠 Comandi**

/check [@/id] = Controlla se un utente è in BlackList [in privato e nei gruppi]
/supporter [@/id o niente] = Controlla se un utente è un supporter [in privato e nei gruppi]
""",        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙Indietro🔙", "info")]
            ]))
        else:
            await message.reply_text("""**🛠 Comandi**

👑 » Fondatore
👮‍♂️ » Amministratori
👤 » Tutti

/check [@/id] = Controlla se un utente è in BlackList [👤 in privato e nei gruppi]
/stats = Statistiche bot [👮‍♂️ 👑 in privato e nei gruppi]
/supporter [@/id o niente] = Controlla se un utente è un supporter [👤 in privato e nei gruppi]
/admin [@/id] = Aggiunge un admin [👑 in privato e nei gruppi]
/unadmin [@/id] = Toglie un admin [👑 in privato e nei gruppi]
/netban [@/id linkProve motivo] = Banna un'utente [👮‍♂️ 👑 in privato e nei gruppi]
/netunban [@/id] = Sbanna un'utente [👮‍♂️ 👑 in privato e nei gruppi]
/post [messaggio] = Post globale [👑 in privato]
/cmd = ti dice i comandi [👤]
/supporto = puoi mandare un supporto [👤 nei gruppi]

""")

@client.on_callback_query()
async def button(client, query):
    user = query.from_user
    if query.data == "info":
        await query.answer("ℹ️")
        await query.message.edit(f"""ℹ️ **Informazioni**

{me.mention} è nato il 19 Novembre 2021, ha lo scopo di togliere gli utenti pericolosi dal tuo gruppo.

👨🏻‍🔧**Staff:**

{await staff()}

__• Rigraziamo gli utenti del nostro bot perchè senza di loro nulla sarebbe possibile__.""", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🛠 Comandi", "cmd"), InlineKeyboardButton("Novità 📣", url="https://t.me/LTSAntiScam_Channel")],
        [InlineKeyboardButton("🔙Indietro🔙", "hm")]
        ]))
    elif query.data == "staffcts":
        founder1 = await client.get_users(5339624520)
        founder2 = await client.get_users(573958069)
        founder3 = await client.get_users(2100381021)
        vicefounder = await client.get_users(5342417758)
        tex = ""
        for ad, in conn.cursor().execute("SELECT chat_id FROM admin").fetchall():
            adm = await client.get_users(ad)
            tex += f"➥ {adm.mention}\n\n"
        await query.message.edit(f"""      
⚙ Lista staff di {me.mention}

👑 Owner
➥ {founder3.mention}
➥ {founder1.mention}
➥ {founder2.mention}

⚜️ Vice-Owner
➥ {vicefounder.mention}

👮‍♂️ Supporter
{tex}
""", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙Indietro🔙", "hm")]]))
    elif query.data == "close_supporto":
        await query.message.edit(f"Supporto risolto da {query.from_user.mention}")
    elif query.data == "hm":
        await query.answer("🏠")
        await query.message.edit(await message_start(user), reply_markup=await keyboard_start())
    elif query.data == "cmd":
        await query.answer("🛠")
        if not isAdmin(user.id):
            await query.message.edit("""**🛠 Comandi**

/check [@/id] = Controlla se un utente è in BlackList [in privato e nei gruppi]
/supporter [@/id o niente] = Controlla se un utente è un supporter [in privato e nei gruppi]
""",        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙Indietro🔙", "info")]
            ]))
        else:
            await query.message.edit("""**🛠 Comandi**

👑 » Fondatore
👮‍♂️ » Amministratori
👤 » Tutti

/check [@/id] = Controlla se un utente è in BlackList [👤 in privato e nei gruppi]
/stats = Statistiche bot [👮‍♂️ 👑 in privato e nei gruppi]
/supporter [@/id o niente] = Controlla se un utente è un supporter [👤 in privato e nei gruppi]
/admin [@/id] = Aggiunge un admin [👑 in privato e nei gruppi]
/unadmin [@/id] = Toglie un admin [👑 in privato e nei gruppi]
/netban [@/id linkProve motivo] = Banna un'utente [👮‍♂️ 👑 in privato e nei gruppi]
/netunban [@/id] = Sbanna un'utente [👮‍♂️ 👑 in privato e nei gruppi]
/post [messaggio] = Post globale [👑 in privato]
/cmd = ti dice i comandi [👤]
""",        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙Indietro🔙", "info")]
            ]))
async def message_start(user):
    return f"""
👋🏻 Benvenuto {user.mention},
🚷 {me.mention} é un bot che banna gli utenti pericolosi dal tuo gruppo.
👉🏻 Aggiungimi al tuo gruppo come admin.
ℹ️ Per più info clicca il bottone **Informazioni**
"""
async def keyboard_start():
    key = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Aggiugimi ad un gruppo ➕", url=f"https://t.me/{me.username}?startgroup=start")],
    [InlineKeyboardButton("🗂 Archivio", url="https://t.me/CTSArchivio"), InlineKeyboardButton("Staff 👮🏻‍♂", "staffcts")],
    [InlineKeyboardButton("🚨 Segnala 🚨", url="https://t.me/CTSAssistenzaBot")],
    ])
    return key
async def message_netban(ban_id, admin_id, motivo):
    ban_info = await client.get_users(ban_id)
    admin_info = await client.get_users(admin_id)
    return f"""
➕Nuovo utente inserito in BlackList

👨🏽‍💻Informazioni sull'utente
Nome: {ban_info.mention}
Username: @{ban_info.username}
ID: {ban_id}

👮🏼‍♂️Bannato da
Nome: {admin_info.mention}
Username: @{admin_info.username} 
ID: {admin_id}

📠 Motivazione
➥ {motivo}

🗂 Prove: <a href='https://t.me/CTSArchivio'>Clicca Qui</a>
"""
async def message_unban(ban_id):
    ban_info = await client.get_users(ban_id)
    return f"""
➖Utente rimosso dalla BlackList

👨🏽‍💻Informazioni Utente
Nome: {ban_info.mention}
Menzione: @{ban_info.username}
ID: {ban_id}

💡Lo staff si scusa per il disagio.
"""
def isUserandAdd(user_id: int):
    result = conn.cursor().execute("SELECT * FROM user WHERE chat_id = ?", [user_id])
    if len(result.fetchall()) > 0:
        pass
    else:
        conn.cursor().execute("INSERT INTO user (chat_id) VALUES (?)", [user_id])
        conn.commit()
def isAdmin(user_id):
    result = conn.cursor().execute("SELECT chat_id FROM admin WHERE chat_id = ?", [user_id])
    if len(result.fetchall()) > 0 or user_id in dev or user_id in founder:
        return True
    else:
        return False
def checker(user_id):
    result = conn.cursor().execute("SELECT userid FROM netban WHERE userid = ?", [user_id])
    if len(result.fetchall()) > 0:
        return True
    else:
        return False
def get_info_netban(user_id):
    result = conn.cursor().execute("SELECT motivo FROM netban WHERE userid = ?", [user_id]).fetchone()[0]
    return {"motivo": result}
def addGroup(id):
    result = conn.cursor().execute("SELECT chat_id FROM gruppi WHERE chat_id = ?", [id])
    if len(result.fetchall()) > 0:
        pass
    else:
        conn.cursor().execute("INSERT INTO gruppi (chat_id) VALUES (?)", [id])
        conn.commit()
async def staff():
    founder = await client.get_users(5339624520)
    founder2 = await client.get_users(573958069)
    developer = await client.get_users(5342417758)
    text = ""
    for a, in conn.cursor().execute("SELECT chat_id FROM admin").fetchall():
        admin = await client.get_users(a)
        text += f"• 👮‍♂ Admin {admin.mention}\n\n"
    return f"• 👑 Founder {founder.mention}, {founder2.mention}\n\n{text}• 🧑‍💻 Developer {developer.mention}"


idle()