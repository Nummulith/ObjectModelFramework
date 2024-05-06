import cProfile
from Y3A.Y3A import Test

profile = cProfile.Profile()
profile.enable()

Test()

profile.disable()

profile.dump_stats('profile_results.prof')
