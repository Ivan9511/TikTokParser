from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)
executor2 = ThreadPoolExecutor(max_workers=1)

s_ids = [549688410, 547711860, 543331562, 548551298, 536812226, 497395160, 536812293, 552287241, 543331560, 548214770, 534723034, 534723036, 534723037, 534723038, 534723039]

def parse(s_id):
    if s_id in s_ids:
        print("Поток 1")
    else:
        print("Поток 2")

parse(549688410)
parse(549288410)