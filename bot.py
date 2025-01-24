import os
import discord
from discord.ext import commands
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json 

TOKEN = 'TOKEN'
TEMPLATES_FOLDER = 'TEMPLATES_FOLDER'  # Template folder path
PLACEHOLDERS_FOLDER = 'PLACEHOLDERS_FOLDER'  # Placeholders folder path
SMTP_SERVER = 'SMTP_SERVER'
SMTP_PORT = 587
SMTP_USER = 'SMTP_USER'
SMTP_PASSWORD = 'SMTP_PASSWORD'

PROMPTS_FILE = 'PROMPTS.JSON'


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def load_placeholders(template_name):
    placeholders = {}
    placeholder_file = os.path.join(PLACEHOLDERS_FOLDER, f"{template_name}.txt")
    
    if os.path.exists(placeholder_file):
        with open(placeholder_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Ignore empty lines
                    placeholders[line] = ""  # Initialize placeholder without value
    return placeholders

def load_placeholder_prompts(template_name):
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r') as file:
            all_prompts = json.load(file)
        return all_prompts.get(template_name, {})
    return {}

def replace_placeholders(template_content, placeholders, user_placeholders):
    for placeholder, value in user_placeholders.items():
        # Replace placeholder with the user value
        template_content = template_content.replace(placeholder, value)
    return template_content


def send_email(spoof_email, recipient_email, subject, html_content):
    msg = MIMEMultipart('alternative')
    msg['From'] = spoof_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(spoof_email, recipient_email, msg.as_string())


@bot.command()
async def generate(ctx):
    # template configs
    templates = {
        1: {"name": "balenciaga", "email": "SMTP_EMAIL", "subject": "Order #ORDERNUMBER confirmed"}, # done #logo # prompts done
        2: {"name": "corteiz", "email": "SMTP_EMAIL", "subject": "Order #{{ORDER_NUMBER}} confirmed"}, # done # prompts undone
        3: {"name": "bape", "email": "SMTP_EMAIL", "subject": "Order #ORDER_NUMBER confirmed"}, # done # logo # prompts undone
        4: {"name": "amazon", "email": "SMTP_EMAIL", "subject": "Order #ORDER_NUMBER confirmed"}, # done # logo # prompts undone
        5: {"name": "stockx", "email": "SMTP_EMAIL", "subject": "🎉 Order Delivered! PRODUCT_NAME (SIZE)"}, # done # prompts undone
        6: {"name": "farfetch", "email": "SMTP_EMAIL", "subject": "Your order will be with you soon"}, # done # logo # prompts undone
        7: {"name": "moncler ", "email": "SMTP_EMAIL", "subject": "Thank you for your order"}, # done # logo # prompts undone
        8: {"name": "dior", "email": "SMTP_EMAIL", "subject": "Your order confirmation"}, #done # logo # prompts undone
        9: {"name": "Nike", "email": "SMTP_EMAIL", "subject": "Thank You for Your Order #ORDER_NUMBER"}, #done # logo # prompts undone
        9: {"name": "Supreme", "email": "SMTP_EMAIL", "subject": "online shop order"}, #done # logo # prompts undone
        10: {"name": "Ebay", "email": "SMTP_EMAIL", "subject": "Your purchase is confirmed"}, # done # logo # prompts undone
        11: {"name": "Apple", "email": "SMTP_EMAIL", "subject": "We're processing your order ORDERNUMBER"}, # done # prompts undone
        12: {"name": "Louis Vuitton", "email": "SMTP_EMAIL", "subject": "Your Louis Vuitton Order Has been Shipped"}, # prompts done
        13: {"name": "SOON!", "email": "SMTP_EMAIL", "subject": ""}, # prompts undone
        14: {"name": "Trapstar", "email": "SMTP_EMAIL", "subject": "Your Trapstar order has been placed"}, # prompts undone
        15: {"name": "", "email": "SMTP_EMAIL", "subject": "Your Order Order invoice #ORDER_NUMBER"}, # prompts undone
        16: {"name": "Dyson", "email": "SMTP_EMAIL", "subject": "Your Dyson order confirmation order_number" }, # prompts undone
        17: {"name": "Goat", "email": "SMTP_EMAIL", "subject": "Your GOAT order #order_number"}, # prompts undone
        18: {"name": "Prada", "email": "SMTP_EMAIL", "subject": "Prada - Order acknowledgement - order_number"}, # prompts undone
        19: {"name": "Grailed", "email": "SMTP_EMAIL", "subject": "Congrats on your purchase!"}, # prompts undone
        20: {"name": "Media Expert", "email": "SMTP_EMAIL", "subject": "tutaj cos bedzie"}, # prompts undone
        21: {"name": "OffWhite", "email": "SMTP_EMAIL", "subject": "your pandabuy package has been seized"}, # prompts undone
    }

    if "★ customer" not in [role.name for role in ctx.author.roles]:
        await ctx.send("You don't have permission to use this command.")
        return

    template_list = "\n".join([f"[{idx}] {config['name']}" for idx, config in templates.items()])
    embed = discord.Embed(title="Available Templates", description=template_list, color=discord.Color.purple())
    await ctx.send(embed=embed)

    def check_message(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check_message, timeout=60.0)
        template_choice = int(msg.content)
        selected_template = templates.get(template_choice)

        if not selected_template:
            await ctx.send("Invalid choice. Please try again.")
            return

        template_name = selected_template['name']
        template_file = f"{template_name}.html"
        with open(os.path.join(TEMPLATES_FOLDER, template_file), 'r') as file:
            template_content = file.read()

        
        placeholders = load_placeholders(template_name)
        placeholder_prompts = load_placeholder_prompts(template_name)

       
        user_placeholders = {}
        for placeholder in placeholders.keys():
            prompt_message = placeholder_prompts.get(placeholder, f"Enter value for {placeholder} (or type 'skip' to leave blank):")
            await ctx.send(prompt_message)
            msg = await bot.wait_for('message', check=check_message, timeout=60.0)
            value = msg.content
            if value.lower() != 'skip':
                user_placeholders[placeholder] = value

        
        updated_content = replace_placeholders(template_content, placeholders, user_placeholders)

        
        spoof_email = selected_template['email']
        subject = replace_placeholders(selected_template['subject'], placeholders, user_placeholders)

        
        await ctx.send("Enter the recipient's email address:")
        msg = await bot.wait_for('message', check=check_message, timeout=60.0)
        recipient_email = msg.content

        
        send_email(spoof_email, recipient_email, subject, updated_content)

        await ctx.send("The email has been sent successfully! Remember to check spam before asking support!")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

bot.run(TOKEN)