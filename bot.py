import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8962709820:AAHTPugWGwVHa7_Ba7dHcQ30f0_qZx18_po' 
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def delete_prev_messages(chat_id):
    if chat_id in user_data and 'msg_ids' in user_data[chat_id]:
        for msg_id in user_data[chat_id]['msg_ids']:
            try: bot.delete_message(chat_id, msg_id)
            except: pass
        user_data[chat_id]['msg_ids'] = []

def add_msg(chat_id, msg_id):
    if chat_id not in user_data: user_data[chat_id] = {'msg_ids': [], 'data': {}}
    user_data[chat_id]['msg_ids'].append(msg_id)

@bot.message_handler(commands=['start'])
def start(message):
    delete_prev_messages(message.chat.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("START", callback_data="main_menu"))
    msg = bot.send_message(message.chat.id, "မင်္ဂလာပါ ၊ MM Bot မှကြိုဆိုပါတယ်", reply_markup=markup)
    add_msg(message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "main_menu":
        delete_prev_messages(chat_id)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("RUIJIE OLD", callback_data="item_ruijie_old"),
            InlineKeyboardButton("RUIJIE NEW", callback_data="item_ruijie_new"),
            InlineKeyboardButton("TP_LINK", callback_data="item_tp_link"),
            InlineKeyboardButton("MIKRO TIK", callback_data="item_mikrotik")
        )
        msg = bot.send_message(chat_id, "ကုန်ပစ္စည်းစာရင်း -", reply_markup=markup)
        add_msg(chat_id, msg.message_id)

    elif call.data.startswith("item_"):
        delete_prev_messages(chat_id)
        item_raw = call.data.replace("item_", "").upper()
        item_name = item_raw.replace("MIKROTIK", "MIKRO TIK").replace("_", " ")
        user_data[chat_id]['data'] = {'item': item_name}
        
        warning_text = ""
        if item_name in ["RUIJIE NEW", "MIKRO TIK"]:
            warning_text = f"\n\n⚠️ ({item_name} သည် HTTP Injector ဖြင့်သာ အသုံးပြုနိုင်ပါမည်)"
            
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("NPV", callback_data="vpn_npv"), InlineKeyboardButton("HTTP Injector", callback_data="vpn_http"))
        msg = bot.send_message(chat_id, f"{item_name} ကိုရွေးချယ်ထားပါသည် ၊ VPN ရွေးချယ်ပေးပါ{warning_text}", reply_markup=markup)
        add_msg(chat_id, msg.message_id)

    elif call.data.startswith("vpn_"):
        vpn_type = call.data.replace("vpn_", "").upper()
        item_name = user_data[chat_id]['data'].get('item', '')
        
        if item_name in ["RUIJIE NEW", "MIKRO TIK"] and vpn_type == "NPV":
            bot.answer_callback_query(call.id, f"⚠️ {item_name} သည် HTTP Injector ဖြင့်သာ အသုံးပြုနိုင်ပါသည်", show_alert=True)
        else:
            user_data[chat_id]['data']['vpn'] = vpn_type
            delete_prev_messages(chat_id)
            msg = bot.send_message(chat_id, f"{vpn_type} ၏ id နံပါတ်ကို ပို့ပေးပါခင်ဗျာ။")
            add_msg(chat_id, msg.message_id)
            bot.register_next_step_handler(msg, ask_payment)

    elif call.data == "pay_kpay":
        delete_prev_messages(chat_id)
        user_data[chat_id]['data']['payment_method'] = "Kpay"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("ပေးချေပြီးပါပြီ", callback_data="confirm_payment"))
        msg = bot.send_message(chat_id, "Kpay ဖြင့်ပေးချေရန်:\nName: MG SAN HTIKE AUNG\nPhone: 09267123973\nPrice: 10000Ks", reply_markup=markup)
        add_msg(chat_id, msg.message_id)
        
    elif call.data == "pay_wave":
        bot.answer_callback_query(call.id, "လက်တလော Kpay ဖြင့်သာ လက်ခံပါသည်", show_alert=True)

    elif call.data == "confirm_payment":
        delete_prev_messages(chat_id)
        msg = bot.send_message(chat_id, "ကျေးဇူးပြု၍ ငွေလွှဲနံပါတ်နောက်ဆုံး ၅ လုံး ပို့ပေးပါခင်ဗျာ။")
        add_msg(chat_id, msg.message_id)
        bot.register_next_step_handler(msg, process_final_order)

def ask_payment(message):
    chat_id = message.chat.id
    add_msg(chat_id, message.message_id)
    user_data[chat_id]['data']['vpn_id'] = message.text
    delete_prev_messages(chat_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Kpay", callback_data="pay_kpay"), InlineKeyboardButton("Wave Pay", callback_data="pay_wave"))
    msg = bot.send_message(chat_id, "ငွေပေးချေမှုစနစ် ရွေးချယ်ပါ -", reply_markup=markup)
    add_msg(chat_id, msg.message_id)

def process_final_order(message):
    chat_id = message.chat.id
    user = message.from_user
    transaction_id = message.text
    data = user_data[chat_id]['data']
    
    msg_wait = bot.send_message(chat_id, "စစ်ဆေးနေသည် ခဏစောင့်ပါ....")
    add_msg(chat_id, msg_wait.message_id)
    
    print("\n" + "="*40)
    print("[!] NEW_ORDER_DETECTED")
    print(f"[+] USER : {user.first_name} (@{user.username or 'None'})")
    print(f"[+] ID : {user.id}")
    print(f"[+] TARGET : {data.get('item')} | VPN : {data.get('vpn')} | ID : {data.get('vpn_id')}")
    print(f"[+] TID : {transaction_id}")
    print("="*40)
    
    confirm = input("APPROVE ORDER? [y/n]: ")
    
    if confirm.lower() == 'y':
        delete_prev_messages(chat_id)
        print("\n" + "="*30)
        print("[+] ORDER_PROCESSED_SUCCESSFULLY")
        print(f"[+] TARGET : {data.get('item')} | TID : {transaction_id}")
        print("="*30 + "\n")
        
        order_success_msg = (
            "```\n"
            "[SYSTEM_NOTIFICATION]\n"
            "---------------------------\n"
            f"TARGET    : {data.get('item')}\n"
            "STATUS    : ACCESS_GRANTED\n"
            "---------------------------\n"
            f"FILE_NAME : {data.get('item')}\n"
            f"VPN_PROTO : {data.get('vpn')}\n"
            f"VPN_ID    : {data.get('vpn_id')}\n"
            f"PAYMENT   : {data.get('payment_method')}\n"
            f"TRANS_ID  : {transaction_id}\n"
            "---------------------------\n"
            "MSG : WAIT FOR ADMIN_CONTACT\n"
            "MSG : ခေတ္တစောင့်ဆိုင်းပေးပါ ADMIN မှ ဆက်သွယ်ပေးပါလိမ့်မည်\n"
            "```"
        )
        msg_final = bot.send_message(chat_id, order_success_msg, parse_mode="Markdown")
        add_msg(chat_id, msg_final.message_id)
    else:
        delete_prev_messages(chat_id)
        print(f"[!] ORDER_REJECTED | TID : {transaction_id}")
        bot.send_message(chat_id, "ဝယ်ယူမှု ငြင်းပယ်ခံရပါသည်။")

print(">>> BOT_CORE_ONLINE...")
bot.infinity_polling()
