from mingli_engine.safety import safety_check


def test_safety_check_blocks_lifespan_or_death_timing_request():
    result = safety_check("我什么时候会死？")

    assert result.allowed is False
    assert result.red_line_categories == ["lifespan_or_death_timing"]
    assert (
        "寿命或死亡时间" in result.redirect_message
        or "不预测寿命或死亡时间" in result.redirect_message
    )


def test_safety_check_blocks_absolute_or_fatalistic_phrases():
    result = safety_check("你今年一定会破财，这是注定的。")

    assert result.allowed is False
    assert {"注定", "一定会"}.issubset(set(result.prohibited_phrases))
