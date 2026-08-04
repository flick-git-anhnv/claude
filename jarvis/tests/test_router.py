from jarvis import Route, Router, Task


def test_higher_priority_route_wins():
    router = Router(default_agents=["fallback"])
    router.add(Route.keyword(name="low", agents=["a"], keywords=["foo"], priority=1))
    router.add(Route.keyword(name="high", agents=["b"], keywords=["foo"], priority=10))

    route, agents = router.resolve(Task(input="foo bar"))
    assert route.name == "high"
    assert agents == ["b"]


def test_falls_back_to_default_when_nothing_matches():
    router = Router(default_agents=["fallback"])
    router.add(Route.keyword(name="only", agents=["a"], keywords=["specific"]))

    route, agents = router.resolve(Task(input="unrelated text"))
    assert route is None
    assert agents == ["fallback"]


def test_keyword_match_is_case_insensitive():
    router = Router()
    router.add(Route.keyword(name="greet", agents=["echo"], keywords=["hello"]))

    route, agents = router.resolve(Task(input="HELLO there"))
    assert route.name == "greet"
