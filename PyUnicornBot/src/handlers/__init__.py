from . import common, baby, numbers, admin, blackjack, profile

routers = [admin.router,
           common.router,
           baby.router,
           blackjack.router,
           numbers.router,
           profile.router]
