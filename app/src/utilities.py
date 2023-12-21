


import os
import asyncio
import time

# Function to remove the expired files
async def delete_expired_files():
    temp_files_directory = os.getcwd() + "\\app\\temp_folder"  # directory to look into
    expiration_duration = 24 * 60 * 60  # 24 hours in seconds
    #expiration_duration = 30 # just to toy with it

    while True:
        for filename in os.listdir(temp_files_directory):
            file_path = os.path.join(temp_files_directory, filename)
            if os.path.isfile(file_path):
                if time.time() - os.path.getmtime(file_path) > expiration_duration:
                    print("Temp files auto-cleaned:")
                    print(f"{file_path}")
                    os.remove(file_path)
        await asyncio.sleep(3600)  # Check every hour (3600 seconds)


