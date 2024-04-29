import cProfile
from omf_aws import Test

profile = cProfile.Profile()
profile.enable()

Test()

profile.disable()

profile.dump_stats('profile_results.prof')
