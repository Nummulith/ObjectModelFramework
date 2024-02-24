import cProfile
from awsScript import Test

profile = cProfile.Profile()
profile.enable()

Test()

profile.disable()

profile.dump_stats('profile_results.prof')
