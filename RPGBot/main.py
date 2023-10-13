import discord
import sqlite3
import random
import time
import os
import random

from discord.ext import tasks

conn = sqlite3.connect('game.db')
c = conn.cursor()

intents = discord.Intents.default()
intents.message_content = True

enemyId = 0

client = discord.Client(intents=intents)

class Enemy:
    enemy_count = 0
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp
        print("Welcome to this world {}!".format(self.name))
        Enemy.enemy_count += 1    
    
    def __del__(self):
        print("Goodbye {} :(".format(self.name))
        Enemy.enemy_count -= 1

@tasks.loop(minutes=1.0, count=None)
async def update_cooldowns():
    print("Updating player cooldowns...")
    c.execute('UPDATE player_list SET movement = movement + .5 WHERE movement < 5')
    c.execute('update player_list set stamina = stamina + 1 WHERE stamina < 10')
    conn.commit()

@client.event
async def on_ready():

    print(f'We have logged in as {client.user}')
    c.execute('''CREATE TABLE IF NOT EXISTS map_table (
            id INTEGER,
            name TEXT NOT NULL,
            type INTEGER,
            moveNorth BOOLEAN,
            moveSouth BOOLEAN,
            moveWest BOOLEAN,
            moveEast BOOLEAN,
            enemiesPossible INTEGER,
            treasuresPossible INTEGER,
            rechargeTime INTEGER,
            description TEXT
            )''')
    zones = ["open plains with tall grass", "a mountainous expanse with rocky terrain below", "a forest with dense foliage"]
    zoneDesc = ""
    zoneType = 0
    zoneName = ""
    for tile in range(199):
        zoneType = round(random.random() * 2)
        match zoneType:
            case 0:
                zoneName = "open plains"
                zoneDesc = zones[0]
            case 1:
                zoneName = "mountain pass"
                zoneDesc = zones[1]
            case 2:
                zoneName = "dense forest"
                zoneDesc = zones[2]
        c.execute(f'''INSERT INTO map_table (id,name,type,moveNorth,moveSouth,moveWest,moveEast,enemiesPossible,treasuresPossible,rechargeTime,description) 
                    VALUES ({tile},'{zoneName}',{zoneType},true,true,true,true,5,5,600,'{zoneDesc}')''')
    c.execute('''CREATE TABLE IF NOT EXISTS player_list (
            id PRIMARY KEY,
            name TEXT NOT NULL,
            pow INTEGER,
            con INTEGER,
            dex INTEGER,
            intl INTEGER,
            hp INTEGER,
            mp INTEGER,
            stamina INTEGER,
            movement INTEGER,
            weapon TEXT,
            armor TEXT,
            effect INTEGER,
            experience INTEGER,
            note TEXT,
            location INTEGER,
            ac INTEGER
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS enemy_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pow INTEGER,
            con INTEGER,
            dex INTEGER,
            intl INTEGER,
            hp INTEGER,
            mp INTEGER,
            stamina INTEGER,
            movement INTEGER,
            weapon TEXT,
            armor TEXT,
            effect INTEGER,
            experience INTEGER,
            note TEXT,
            location INTEGER,
            ac INTEGER
            )''')
    c.execute('INSERT INTO enemy_list (name) VALUES ("Blob")')
    c.execute(f'''update enemy_list
            set
            pow = 1,
            con = 1,
            dex = 1,
            intl = 1,
            hp = 10,
            mp = 10,
            stamina = 10,
            movement = 5,
            weapon = "bare hands",
            armor = "none",
            effect = 0,
            experience = 0,
            note = "none",
            location = 70,
            ac = 10''')
    conn.commit()
    update_cooldowns.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    userId = message.author.id

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('!register'):
        
        name = message.content.split(" ")[1]
        print("id", id, "Name:", name)

        c.execute('select id from player_list where id = ?', [userId])
        user_exists = c.fetchone()
        print("Exists?", user_exists)

        if user_exists is None:
            c.execute('select name from player_list where name = ?', [name])
            player_exists = c.fetchone()
            print("Player exists?", player_exists)
            if player_exists is None:
                c.execute('insert into player_list(id, name) values(?,?)', (userId, name))
                startLoc = round(random.random() * 199)
                c.execute(f'''update player_list
                          set 
                          pow = 1,
                          con = 1,
                          dex = 1,
                          intl = 1,
                          hp = 10,
                          mp = 10,
                          stamina = 10,
                          movement = 5,
                          weapon = "bare hands",
                          armor = "none",
                          effect = 0,
                          experience = 0,
                          note = "none",
                          location = {startLoc},
                          ac = 10
                          where id = ?''', [userId])
                conn.commit()
                print('Created', name, userId)
                await message.channel.send(f'Player registered. Name: {name}')
            else:
               await message.channel.send('A player by that name already exists.') 
        else:
            print(name, 'already exists')
            await message.channel.send('You have already registered a player.')

    if message.content.startswith('!status'):
        userId = message.author.id
        c.execute('select * from player_list where id = ?', [userId])
        user_exists = c.fetchone()
        name = user_exists[1]
        pow = user_exists[2]
        con = user_exists[3]
        dex = user_exists[4]
        intl = user_exists[5]
        hp = user_exists[6]
        mp = user_exists[7]
        stamina = user_exists[8]
        movement = user_exists[9]
        weapon = user_exists[10]
        armor = user_exists[11]
        effect = user_exists[12]
        experience = user_exists[13]
        location = user_exists[15]
        ac = user_exists[16]
        print("Exists?", user_exists)
        print((f'{name} pow: {pow}, con {con}, dex {dex}, intl, {intl}, hp {hp}, mp {mp}, stamina {stamina}, movement {movement}, weapon {weapon}, armor {armor}, AC {ac}, effect {effect}, experience {experience}. Location: {location}'))
        await message.channel.send(f'{name} pow: {pow}, con {con}, dex {dex}, intl, {intl}, hp {hp}, mp {mp}, stamina {stamina}, movement {movement}, weapon {weapon}, armor {armor}, AC {ac}, effect {effect}, experience {experience}. Location: {location}')

    if message.content.startswith('!location'):
            userId = message.author.id
            c.execute('select * from player_list where id = ?', [userId])
            user_exists = c.fetchone()
            location = user_exists[15]
            c.execute('select * from map_table where id = ?', [location])
            zone = c.fetchone()
            zoneDesc = zone[10]
            print("Exists?", user_exists)
            print((f"You see {zoneDesc} before you. You are in space {location}"))
            enemy = c.execute('SELECT * from enemy_list where location = ?', [location])
            print(location)
            print(enemy.rowcount)
            if enemy.rowcount != -1:
                pveEnemy = c.fetchone()
                enemyName = pveEnemy.name
                await message.channel.send((f"You see {zoneDesc} before you. You are in space {location}. A {enemyName} stands in your path."))
            else: await message.channel.send((f"You see {zoneDesc} before you. You are in space {location}."))


    if message.content.startswith('!attack'):
        # Find the player who is attacking
        c.execute('select * from player_list where id = ?', [userId])
        player = c.fetchone()
        stamina = player[8]
        if stamina >= 1:
            location = player[15]
            weapon = player[10]
            targetName = message.content.split(" ")[1]
            # Find a player target
            c.execute('select * from player_list where name = ?', [targetName])
            playerTarget = c.fetchone()
            print(playerTarget)
            if playerTarget:
                targetLoc = playerTarget[15]
                targetName = playerTarget[1]
                print("Found " + targetName)
                print("Target Location: "+ str(targetLoc))
                print("Target Name: "+ targetName)
                if location == targetLoc:
                    c.execute('UPDATE player_list SET stamina = stamina - 1 WHERE id = ?', [userId])
                    conn.commit()
                    await message.channel.send(f"You attack {targetName} with {weapon}!")
                else: 
                    await message.channel.send(f"That target is not here!")
            else:
                pveEnemy = c.execute('select * from enemy_list where name = ?', [targetName])
                pveEnemy = c.fetchone()
                pveName = pveEnemy[1]
                pveLoc = pveEnemy[15]
                print(pveEnemy)
                if pveLoc == location:
                    return await message.channel.send(f"You attack {pveName} with {weapon}!")
                else:
                    await message.channel.send(f"That target is not here!")
        else:
            await message.channel.send(f"You don't have enough stamina!")
    
    if message.content.startswith('!drink'):
        drink = message.content.split(" ")[1]
        await message.channel.send(f"You drink the {drink}")

    if message.content.startswith('!note'):
        note = message.content.split(" ", 1)[1]
        c.execute(f'''update player_list
                        set
                        note = '{note}'
                        where id = ?''', [userId])
        conn.commit()
        await message.channel.send(f"You write '{note}' in your notebook.")

    if message.content.startswith('!readnote'):
        c.execute('select * from player_list where id = ?', [userId])
        note = c.fetchone()[10]
        await message.channel.send(f"You read the note from your notebook: '{note}'")

    if message.content.startswith('!move'):
        c.execute('select * from player_list where id = ?', [userId])
        player = c.fetchone()
        location = player[15]
        direction = message.content.split(" ")[1]
        moveRemain = player[9]
        print(player, location, moveRemain)
        if moveRemain >= 1:
            match direction:
                case "north":
                    c.execute(f'select moveNorth from map_table where id = {location}')
                    targetTile = location - 20
                case "south":
                    c.execute(f'select moveSouth from map_table where id = {location}')
                    targetTile = location + 20
                case "east":
                    c.execute(f'select moveEast from map_table where id = {location}')
                    targetTile = location + 1
                case "west":
                    c.execute(f'select moveWest from map_table where id = {location}')
                    targetTile = location - 1
            c.execute('select * from map_table where id = ?', [targetTile])
            gotTile = c.fetchone()
            canMove = gotTile[0]
            if canMove > -1:
                targetTileName = gotTile[1]
                c.execute(f'update player_list set location = {targetTile} where id =?', [userId])
                moveRemain -= 1
                c.execute(f'update player_list set movement = {moveRemain} where id =?', [userId])
                conn.commit()
                await message.channel.send(f"You move {direction} into {targetTileName}")
            else: await message.channel.send(f"You can't move that way!")
        else: await message.channel.send(f"You are too tired to move! Rest first!")

client.run("MTE0MzU2NzM4NTQyOTgwNzI2Ng.GIy0c1.0KgzKPlZe4QY4-YL0QZqvUUmfOR2-2dQB17jxk")


