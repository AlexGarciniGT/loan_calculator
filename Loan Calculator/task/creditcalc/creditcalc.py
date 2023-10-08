""" Main Module
"""
import math
import configparser
import argparse
import os
from typing import Optional, Union

config_type = configparser.ConfigParser
config_section = configparser.SectionProxy
num = Union[int, float]
diff_dict = dict[int, int]

ERROR_PARAM: str = "Incorrect parameters."
DIFF: str = "diff"
ANNUITY: str = "annuity"


def read_config() -> config_type:
    """ Read config file
    """
    config: config_type = config_type()
    path: str = os.path.join(
        os.path.dirname(__file__),
        "data",
        'config.ini'
    )
    config.read(path)
    return config


def get_section(
        section_name: str,
        config: Optional[config_type] = None) -> config_section:
    """ Get config section
    """
    if config is None:
        __config = read_config()
    else:
        __config = config
    return __config[section_name]


OPTIONS: config_section = get_section("options")
PAYMENT: config_section = get_section("options.payment")
PRINCIPAL: config_section = get_section("options.principal")
PERIODS: config_section = get_section("options.periods")
TYPE: config_section = get_section("options.type.diff")


def manage_options(option) -> None:
    """ Admin options
    """
    global PAYMENT, PRINCIPAL, PERIODS, TYPE

    def interest(i: num) -> float:
        """ Indicate the interest rate.
        """
        _i = int(i) if isinstance(i, int) else float(i)
        return _i / (12 * 100)

    def over_payment(A: int, P: int, n: int) -> str:
        overpay: int = int((n * A) - P)
        return OPTIONS.get("overpayment").format(overpayment=overpay)

    def set_n() -> str:
        """ Indicate the years and months periods.
        """
        __i: float = interest(option.interest)
        A: num = int(option.payment) if isinstance(option.payment, int) else float(option.payment)
        P: num = int(option.principal) if isinstance(option.principal, int) else float(option.principal)
        n: dict[str, int] = number_payments(A=A, P=P, i=__i)

        _n: int = sum([(n["year"] * 12), n["month"]])
        overpayment: str = over_payment(A=A, P=P, n=_n)

        if n["year"] > 0:
            pre_mssg: str =  PERIODS.get("years_months").format(year=n["year"], month=n["month"])
        else:
            pre_mssg: str = PERIODS.get("months").format(month=n["month"])

        _mssg: str = "\n".join([pre_mssg, overpayment])
        return _mssg

    def set_a() -> str:
        """ Indicate the annuity payment.
        """
        __i: float = interest(option.interest)

        P: num = int(option.principal) if isinstance(option.principal, int) else float(option.principal)
        n: int = int(option.periods)
        A: int = annuity_payment(P=P, i=__i, n=n)

        overpayment: str = over_payment(A=A, P=P, n=n)

        pre_mssg: str = PAYMENT.get("answer").format(A=A)
        _mssg: str = "\n".join([pre_mssg, overpayment])
        return _mssg

    def set_p() -> str:
        """ Indicate the loan principal.
        """
        __i: float = interest(option.interest)

        A: num = int(option.payment) if isinstance(option.payment, int) else float(option.payment)
        n: int = int(option.periods)
        P: int = loan_principal(A=A, i=__i, n=n)

        overpayment: str = over_payment(A=A, P=P, n=n)
        pre_mssg: str = PRINCIPAL.get("answer").format(P=P)
        _mssg: str = "\n".join([pre_mssg, overpayment])
        return _mssg

    def set_diff() -> str:
        """  Indicate the differentiated  payment
        """
        __i: float = interest(option.interest)
        P: num = int(option.principal) if isinstance(option.principal, int) else float(option.principal)
        n: int = int(option.periods)
        m: int = n
        Dm: diff_dict = dict(sorted(diff_payments(P=P, m=m, i=__i, n=n).items()))
        pre_mssg: list[str] = [TYPE.get("answer").format(month=month, amount=amount)
                               for month, amount in Dm.items()]
        overpay: int = int(sum([amount for amount in Dm.values()]) - P)
        overpayment: str = OPTIONS.get("overpayment").format(overpayment=overpay)
        _mssg: str = "\n\n".join(["\n".join(pre_mssg), overpayment])
        return _mssg

    values: list[str] = [option.payment, option.principal, option.interest, option.periods]
    n_values: list[str] = [option.payment, option.principal, option.interest]
    a_values: list[str] = [option.periods, option.principal, option.interest]
    p_values: list[str] = [option.payment, option.periods, option.interest]

    def no_negative(list_to_check: list[str]) -> bool:
        """ Check if all values are positive.
        """
        for value in list_to_check:
            if not value:
                continue
            _value = int(value) if isinstance(value, int) else float(value)
            if _value < 0:
                return False
        return True

    if  not no_negative(values):
        mssg: str = ERROR_PARAM

    elif option.type == ANNUITY and all(n_values):
        mssg: str = set_n()

    elif option.type == ANNUITY and all(a_values):
        mssg: str = set_a()

    elif option.type == ANNUITY and all(p_values):
        mssg: str = set_p()

    elif option.type == DIFF and all(a_values):
        mssg: str = set_diff()

    else:
        mssg: str = ERROR_PARAM

    print(mssg)


def annuity_payment(P: num,
                    i: float,
                    n: int) -> int:
    """ Calculate annuity payment

    :param P: loan principal
    :param i: nominal (monthly) interest rate.
    :param n: number of payments
    :return: annuity payment
    """
    dividend: num = (i * math.pow((1 + i), n))
    divisor: num = (math.pow((1 + i), n) - 1)
    return math.ceil(P * (dividend / divisor))


def loan_principal(A: num,
                   i: float,
                   n: int
                   ) -> int:
    """ Calculate loan principal

    :param A: annuity payment
    :param i: nominal (monthly) interest rate.
    :param n: number of payments
    :return: loan principal
    """
    dividend: num = (i * math.pow((1 + i), n))
    divisor: num = (math.pow((1 + i), n) - 1)
    return math.ceil(A / (dividend / divisor))


def number_payments(A: num,
                    P: num,
                    i: float) -> dict[str, int]:
    """ Calculate number of payments

    :param A: annuity payment
    :param P: loan principal
    :param i: nominal (monthly) interest rate.
    :return: number of payments
    """
    dividend: num = A
    divisor: num = (A - (i * P))
    n: int = abs(math.ceil(
        math.log(
            (dividend / divisor), (1 + i)
        )
    ))
    return {"year": n // 12, "month": n % 12}


def diff_payments(P: num,
                  m: int,
                  i: float,
                  n: int) -> diff_dict:
    """ calculate differentiated payments.
    """
    if m == 0:
        return {0: 0}
    _m: int = m - 1
    P_n: num = P / n
    dividend: num = (P * (m - 1))
    divisor: num = n
    Dm: int = math.ceil(P_n + i * (P - (dividend / divisor)))
    month: diff_dict = diff_payments(P=P, m=_m, i=i, n=n)

    if month == {0: 0}:
        return {m: Dm}
    _Dm: diff_dict = {m: Dm}
    _Dm.update(month)
    return _Dm


def program() -> None:
    """ Main program
    """
    global OPTIONS
    parser = argparse.ArgumentParser()
    parser.add_argument("--payment",
                        action="store")
    parser.add_argument("--principal",
                        action="store")
    parser.add_argument("--periods",
                        action="store")
    parser.add_argument("--interest",
                        action="store")
    parser.add_argument("--type", choices=[DIFF, ANNUITY])

    try:
        options = parser.parse_args()
        manage_options(options)
    except BaseException:
        print(ERROR_PARAM)


def main() -> None:
    program()


if __name__ == '__main__':
    main()
