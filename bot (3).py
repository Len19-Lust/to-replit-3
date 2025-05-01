import discord
from discord.ext import commands
from PIL import Image
import cv2
import numpy as np
import os
from datetime import datetime
from flask import Flask
import threading

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

def detect_settings_button(image_path):
    """Automatically detect the settings button (gear icon) in the provided image."""
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Get the dimensions of the image
    height, width, _ = image.shape

    # Define relative coordinates for the settings button (gear icon)
    settings_button_coords = (
        int(0.85 * width), int(0.80 * height),  # x1, y1
        int(0.98 * width), int(0.95 * height)  # x2, y2
    )

    # Crop the region of interest
    settings_button_crop = image[
        settings_button_coords[1]:settings_button_coords[3],
        settings_button_coords[0]:settings_button_coords[2]
    ]

    # Convert the cropped area to HSV for color detection
    hsv_settings_button = cv2.cvtColor(settings_button_crop, cv2.COLOR_BGR2HSV)

    # Define the range for the color gray (gear icon) in HSV
    lower_gray = np.array([0, 0, 30])  # Extended lower bound for gray
    upper_gray = np.array([180, 50, 220])  # Extended upper bound for gray

    # Create a mask for gray color
    mask_settings_button = cv2.inRange(hsv_settings_button, lower_gray, upper_gray)

    # Find contours in the settings button mask to locate the gear icon
    settings_button_detected = False
    contours, _ = cv2.findContours(mask_settings_button, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        if 0.8 <= aspect_ratio <= 1.2 and w > 10 and h > 10:  # Adjust size thresholds as needed
            settings_button_detected = True
            break

    # Debugging: Save cropped areas and masks for verification
    cv2.imwrite("debug_settings_button_crop_adjusted.png", settings_button_crop)
    cv2.imwrite("debug_settings_button_mask_adjusted.png", mask_settings_button)

    return settings_button_detected

@bot.tree.command(name="verify", description="Upload your game profile.")
async def verify(interaction: discord.Interaction, attachment: discord.Attachment):
    await interaction.response.defer(thinking=True)

    embed_loading = discord.Embed(
        title="⚙️ Verifying Your Profile...",
        description="✨ **Commander, hold steady!**\n\n🌟 **This won't take long!** ⏳",
        color=discord.Color.gold())
    embed_loading.set_thumbnail(
        url="https://www.rok.guide/wp-content/uploads/2020/10/rise-of-kingdoms-wallpaper-1.jpg")
    embed_loading.set_footer(
        text="💡 Powered by Lust Store | 🛡️ Contact Support: @lustyboy | 🚀 Ready to Conquer!")
    loading_message = await interaction.followup.send(embed=embed_loading, wait=True)

    if not attachment:
        error_embed = discord.Embed(
            title="❌ Error: No Image Uploaded",
            description="**Commander, I need your profile image to verify your alliance membership.**",
            color=discord.Color.red())
        error_embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/512/1828/1828659.png")
        await loading_message.edit(embed=error_embed)
        return

    file_path = f"temp_{interaction.user.id}.png"
    await attachment.save(file_path)

    try:
        # Perform detection
        settings_button_detected = detect_settings_button(file_path)

        if not settings_button_detected:
            error_embed = discord.Embed(
                title="🚫 Verification Failed",
                description=(
                    "⛔ **This's not your game profile. Stop trying to sneak in!**\n\n"
                    "📂 **Make sure to upload a valid screenshot of your game profile.**"
                ),
                color=discord.Color.red())
            error_embed.set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/512/594/594846.png")
            error_embed.add_field(
                name="📋 What You Need to Do:",
                value=(
                    "1️⃣ Ensure your profile screenshot includes the **settings button (gear icon)** at the bottom-right corner.\n"
                    "2️⃣ Avoid cropping the profile details.\n"
                    "3️⃣ Recheck and retry with a valid image."
                ),
                inline=False
            )
            error_embed.set_footer(
                text="💡 Powered by Lust Store | Need help? Contact: @lustyboy | 🚀 Let's Get Verified!")
            await loading_message.edit(embed=error_embed)
            return

        success_embed = discord.Embed(
            title="✅ Verification Successful!",
            description="🎉 **Commander, your profile has been successfully verified!**",
            color=discord.Color.green())
        success_embed.set_thumbnail(
            url="https://www.rok.guide/wp-content/uploads/2020/10/rise-of-kingdoms-wallpaper-2.jpg")
        success_embed.set_image(
            url="https://path-to-your-server-or-cdn-for-image/3751.png")  # Replace with the URL of the provided image
        success_embed.set_footer(
            text="Powered by Lust Store",
            icon_url="https://path-to-your-server-or-cdn-for-logo/lust-store-logo.png")  # Replace with the URL of the Lust Store logo
        await loading_message.edit(embed=success_embed)

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    keep_alive()
    bot.run(TOKEN)