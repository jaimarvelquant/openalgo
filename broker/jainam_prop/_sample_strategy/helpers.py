import datetime as dt


def get_strike(token, exch_data, ltp_func, leg, port, strategy, account_to_use):
    str_dis_map = {
        "NIFTY": 50,
        "BANKNIFTY": 100,
        "FINNIFTY": 50,
        "MIDCPNIFTY": 25,
        "CRUDEOIL": 50,
        "NATURALGAS": 5,
        "GOLDM": 100,
        "SILVERM": 250
    }

    underlying_ltp = ltp_func(strategy, exch_data[0] if port.scrip_type == "INDEX" else exch_data[2], token)
    atm = round(underlying_ltp / str_dis_map[port.scrip]) * str_dis_map[port.scrip]

    if leg.strike_selection_method == "ATM_DISTANCE":
        if leg.ins_type == "CE":
            strike = atm + (leg.atm_distance * str_dis_map[port.scrip])
        elif leg.ins_type == "PE":
            strike = atm - (leg.atm_distance * str_dis_map[port.scrip])

    elif leg.strike_selection_method == "STRADDLE_WIDTH":
        atm_ce_token = account_to_use.master_contract[
            (account_to_use.master_contract["symbol"] == port.scrip) &
            (account_to_use.master_contract["exchange"] == exch_data[2]) &
            (account_to_use.master_contract["option_type"] == "CE") &
            (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
            (account_to_use.master_contract["strike_price"] == atm)
        ].iloc[0].sec_id

        atm_pe_token = account_to_use.master_contract[
            (account_to_use.master_contract["symbol"] == port.scrip) &
            (account_to_use.master_contract["exchange"] == exch_data[2]) &
            (account_to_use.master_contract["option_type"] == "PE") &
            (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
            (account_to_use.master_contract["strike_price"] == atm)
        ].iloc[0].sec_id

        atm_ce_price = ltp_func(exch_data[2], atm_ce_token)
        atm_pe_price = ltp_func(exch_data[2], atm_pe_token)

        atm_straddle_premium = round(atm_ce_price + atm_pe_price, 2)

        if leg.ins_type == "CE":
            base_price = atm + (leg.straddle_width_multiplier * atm_straddle_premium)
        elif leg.ins_type == "PE":
            base_price = atm - (leg.straddle_width_multiplier * atm_straddle_premium)

        strike = round(base_price / str_dis_map[port.scrip]) * str_dis_map[port.scrip]

    elif leg.strike_selection_method == "NEAREST_PREMIUM":
        nearest_premium = leg.nearest_premium + 0.001
        strike = find_strike_by_premium(atm, ltp_func, nearest_premium, str_dis_map, exch_data, account_to_use, leg, port)

    elif leg.strike_selection_method in ("ATM_PRICE_MATCH", "OTM2_PRICE_MATCH"):
        if leg.strike_selection_method == "ATM_PRICE_MATCH":
            base_ce_strike = atm
            base_pe_strike = atm
        elif leg.strike_selection_method == "OTM2_PRICE_MATCH":
            base_ce_strike = atm + 2
            base_pe_strike = atm - 2

        base_ce_token = account_to_use.master_contract[
            (account_to_use.master_contract["symbol"] == port.scrip) &
            (account_to_use.master_contract["exchange"] == exch_data[2]) &
            (account_to_use.master_contract["option_type"] == "CE") &
            (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
            (account_to_use.master_contract["strike_price"] == base_ce_strike)
        ].iloc[0].sec_id

        base_pe_token = account_to_use.master_contract[
            (account_to_use.master_contract["symbol"] == port.scrip) &
            (account_to_use.master_contract["exchange"] == exch_data[2]) &
            (account_to_use.master_contract["option_type"] == "PE") &
            (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
            (account_to_use.master_contract["strike_price"] == base_pe_strike)
        ].iloc[0].sec_id

        base_ce_price = ltp_func(exch_data[2], base_ce_token)
        base_pe_price = ltp_func(exch_data[2], base_pe_token)

        if base_ce_price > base_pe_price:
            if leg.atm_otm_price_match_type == "MATCH_ABOVE":
                # Move to ITM PE Side
                price_to_match = base_ce_price + 0.001
                strike = find_strike_by_premium(base_pe_strike, ltp_func, price_to_match, str_dis_map, exch_data, account_to_use, leg, port, "ITM", "PE")

            elif leg.atm_otm_price_match_type == "MATCH_BELOW":
                # Move to OTM CE Side
                price_to_match = base_pe_price + 0.001
                strike = find_strike_by_premium(base_ce_strike, ltp_func, price_to_match, str_dis_map, exch_data, account_to_use, leg, port, "OTM", "CE")

        elif base_ce_price < base_pe_price:
            if leg.atm_otm_price_match_type == "MATCH_ABOVE":
                # Move to ITM CE Side
                price_to_match = base_pe_price + 0.001
                strike = find_strike_by_premium(base_ce_strike, ltp_func, price_to_match, str_dis_map, exch_data, account_to_use, leg, port, "ITM", "CE")

            elif leg.atm_otm_price_match_type == "MATCH_BELOW":
                # Move to OTM PE Side
                price_to_match = base_ce_price + 0.001
                strike = find_strike_by_premium(base_pe_strike, ltp_func, price_to_match, str_dis_map, exch_data, account_to_use, leg, port, "OTM", "PE")

    elif leg.strike_selection_method == "ATM_DIFFERENCE":
        checking_strike_1 = atm # Will go upwards
        checking_strike_2 = atm # Will go downwards

        least_diff_value = 0
        least_diff_strike = 0

        # 4 means 3 strikes above ATM and below ATM will be checked
        for i in range(4):
            if i == 0:
                # It means ATM
                _diff = get_opt_price_diff_of_strike(checking_strike_1, ltp_func, exch_data, account_to_use, leg, port)

                least_diff_value = _diff
                least_diff_strike = checking_strike_1

            else:
                _diff_1 = get_opt_price_diff_of_strike(checking_strike_1, ltp_func, exch_data, account_to_use, leg, port)
                _diff_2 = get_opt_price_diff_of_strike(checking_strike_2, ltp_func, exch_data, account_to_use, leg, port)

                if _diff_1 < least_diff_value:
                    least_diff_value = _diff_1
                    least_diff_strike = checking_strike_1

                elif _diff_2 < least_diff_value:
                    least_diff_value = _diff_2
                    least_diff_strike = checking_strike_2

            checking_strike_1 = atm + str_dis_map[port.scrip]
            checking_strike_2 = atm - str_dis_map[port.scrip]

        strike = least_diff_strike

    return strike


def find_strike_by_premium(atm, ltp_func, nearest_premium, str_dis_map, exch_data, account_to_use, leg, port, side_to_move="", ins_type=""):
    if ins_type == "":
        ins_type = leg.ins_type

    strike = 0

    atm_token = account_to_use.master_contract[
        (account_to_use.master_contract["symbol"] == port.scrip) &
        (account_to_use.master_contract["exchange"] == exch_data[2]) &
        (account_to_use.master_contract["option_type"] == ins_type) &
        (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
        (account_to_use.master_contract["strike_price"] == atm)
    ].iloc[0].sec_id
    atm_ltp = ltp_func(exch_data[2], atm_token)

    if side_to_move == "":
        if atm_ltp > nearest_premium:
            # Move OTM side
            side_to_move = "OTM"
        elif atm_ltp < nearest_premium:
            # Move ITM side
            side_to_move = "ITM"

    two_strikes = {}
    cur_strike = 0
    prev_strike_ltp = 0

    if side_to_move == "OTM" and ins_type == "CE":
        cur_strike = atm + str_dis_map[port.scrip]
    elif side_to_move == "OTM" and ins_type == "PE":
        cur_strike = atm - str_dis_map[port.scrip]
    elif side_to_move == "ITM" and ins_type == "CE":
        cur_strike = atm - str_dis_map[port.scrip]
    elif side_to_move == "ITM" and ins_type == "PE":
        cur_strike = atm + str_dis_map[port.scrip]

    for i in range(50):
        cur_token = account_to_use.master_contract[
            (account_to_use.master_contract["symbol"] == port.scrip) &
            (account_to_use.master_contract["exchange"] == exch_data[2]) &
            (account_to_use.master_contract["option_type"] == ins_type) &
            (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
            (account_to_use.master_contract["strike_price"] == cur_strike)
        ].iloc[0].sec_id
        cur_strike_ltp = ltp_func(exch_data[2], cur_token)

        if side_to_move == "OTM":
            # Move ITM side
            if cur_strike_ltp > nearest_premium:
                prev_strike_ltp = cur_strike_ltp

                if ins_type == "CE":
                    cur_strike = atm + str_dis_map[port.scrip]
                elif ins_type == "PE":
                    cur_strike = atm - str_dis_map[port.scrip]

            elif cur_strike_ltp < nearest_premium:
                if ins_type == "CE":
                    prev_strike = cur_strike - str_dis_map[port.scrip]
                elif ins_type == "PE":
                    prev_strike = cur_strike + str_dis_map[port.scrip]

                two_strikes = {
                    prev_strike: prev_strike_ltp,
                    cur_strike: cur_strike_ltp
                }

                break

        elif side_to_move == "ITM":
            # Move ITM side
            if cur_strike_ltp < nearest_premium:
                prev_strike_ltp = cur_strike_ltp

                if ins_type == "CE":
                    cur_strike = atm - str_dis_map[port.scrip]
                elif ins_type == "PE":
                    cur_strike = atm + str_dis_map[port.scrip]

            elif cur_strike_ltp > nearest_premium:
                if ins_type == "CE":
                    prev_strike = cur_strike + str_dis_map[port.scrip]
                elif ins_type == "PE":
                    prev_strike = cur_strike - str_dis_map[port.scrip]

                two_strikes = {
                    prev_strike: prev_strike_ltp,
                    cur_strike: cur_strike_ltp
                }

                break

    try:
        diff_1 = abs(leg.nearest_premium - list(two_strikes.values())[0])
        diff_2 = abs(leg.nearest_premium - list(two_strikes.values())[1])

        if diff_1 <= diff_2:
            strike = list(two_strikes.keys())[0]
        elif diff_2 < diff_1:
            strike = list(two_strikes.keys())[1]

    except IndexError:
        # Take prev strike (intentionally reversed)
        if side_to_move == "OTM" and ins_type == "CE":
            strike = cur_strike - str_dis_map[port.scrip]
        elif side_to_move == "OTM" and ins_type == "PE":
            strike = cur_strike + str_dis_map[port.scrip]
        elif side_to_move == "ITM" and ins_type == "CE":
            strike = cur_strike + str_dis_map[port.scrip]
        elif side_to_move == "ITM" and ins_type == "PE":
            strike = cur_strike - str_dis_map[port.scrip]

    return strike


def get_opt_price_diff_of_strike(_str, ltp_func, exch_data, account_to_use, leg, port):
    base_ce_token = account_to_use.master_contract[
        (account_to_use.master_contract["symbol"] == port.scrip) &
        (account_to_use.master_contract["exchange"] == exch_data[2]) &
        (account_to_use.master_contract["option_type"] == "CE") &
        (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
        (account_to_use.master_contract["strike_price"] == _str)
    ].iloc[0].sec_id

    base_pe_token = account_to_use.master_contract[
        (account_to_use.master_contract["symbol"] == port.scrip) &
        (account_to_use.master_contract["exchange"] == exch_data[2]) &
        (account_to_use.master_contract["option_type"] == "PE") &
        (account_to_use.master_contract["expiry_date"] == dt.datetime(leg.expiry.year, leg.expiry.month, leg.expiry.day, 0, 0, 0)) &
        (account_to_use.master_contract["strike_price"] == _str)
    ].iloc[0].sec_id

    base_ce_price = ltp_func(exch_data[2], base_ce_token)
    base_pe_price = ltp_func(exch_data[2], base_pe_token)

    return abs(base_ce_price - base_pe_price)