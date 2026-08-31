from . import common, baby, numbers, admin, blackjack

routers = [admin.router,
           common.router,
           baby.router,
           blackjack.router,
           numbers.router]
