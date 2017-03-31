class Car:
    car_ids = {
        403:'Dominus',
        23:'Octane',
        22:'Breakout',
        24:'Paladin',
        30:'Merc',
        404:'Scarab',
        28:'X-Devil',
        }
    car_hitbox = {
        # car:[length,width,height]
        'Backfire': [117.16,84.67,31.39],
        'Breakout': [135.99,71.85,30.30],
        'DeLorean': [123.94,83.28,29.80],
        'Dominus': [123.94,83.28,29.80],
        'Gizmo': [122.74,94.28,40.67],
        'Grog': [114,81.88,36.93],
        'Hotshot': [123.94,74.28,29.80],
        'Merc': [115.4,70.13,40.27],
        'Octane': [118.01,84.20,39.16],
        'Paladin': [120.25,72.38,29.80],
        'Ripper': [135.12,79.10,37.93],
        'Road Hog': [117.16,84.67,31.39],
        'Scarab': [100.90,82.75,39.17],
        'Takumi': [116,82.27,36.80],
        'Venom': [121.16,75.05,34.30],
        'X-Devil': [115.13,85.74,27.26],
        'Zippy': [118.01,84.20,33.16],
        }

    @classmethod
    def get_hitbox(cls, player):
        # print(player.properties)
        # take loadout 1 as both loadouts should have the same body
        car_id = player.properties['TAGame.PRI_TA:ClientLoadouts']['Value']['Loadout1']['Value']['Body']['Id']
        car_name = player.properties['TAGame.PRI_TA:ClientLoadouts']['Value']['Loadout1']['Value']['Body']['Name']
        try:
            car = cls.car_ids[car_id]
        except KeyError:
            print('Unknown Car (Name: %s, Id: %s). Using Octane.' % (car_name, car_id))
            car = 'Octane'
        car_hitbox = cls.car_hitbox[car]
        return car_hitbox

