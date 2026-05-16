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


def test_safety_check_allows_safe_disclaimer_with_absolute_phrase():
    result = safety_check("本报告不保证一定会发生，仅供自我观察。")

    assert result.allowed is True
    assert result.prohibited_phrases == []


def test_safety_check_allows_non_predictive_lifespan_statement():
    result = safety_check("本报告不预测寿命，只讨论风险意识和生活安排。")

    assert result.allowed is True
    assert result.red_line_categories == []


def test_safety_check_blocks_later_unsafe_phrase_after_safe_disclaimer():
    result = safety_check("本报告不保证一定会发生，但你今年一定会破财。")

    assert result.allowed is False
    assert "一定会" in result.prohibited_phrases


def test_safety_check_blocks_later_lifespan_prediction_after_safe_disclaimer():
    result = safety_check("本报告不预测寿命，但你想让我预测寿命也可以。")

    assert result.allowed is False
    assert result.red_line_categories == ["lifespan_or_death_timing"]
