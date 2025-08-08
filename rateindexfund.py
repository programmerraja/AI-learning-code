import numpy as np
import requests


class IndexFundRater:
    def __init__(self, scheme_code):
        self.scheme_code = scheme_code
        self.fund_data = self.fetch_fund_data()

    def fetch_fund_data(self):
        """Fetch mutual fund data from AMFI or NSE India."""
        try:
            url = f"https://api.mfapi.in/mf/{self.scheme_code}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()

                # Process NAV history
                nav_history = [
                    {"date": entry["date"], "nav": float(entry["nav"])}
                    for entry in data.get("data", [])
                ]

                # Calculate annualized return (simplified example)
                if len(nav_history) > 1:
                    initial_nav = nav_history[-1]["nav"]
                    final_nav = nav_history[0]["nav"]
                    annual_return = ((final_nav - initial_nav) / initial_nav) * 100
                else:
                    annual_return = 0

                return {
                    "annual_return": annual_return,
                    "expense_ratio": 0,  # Placeholder, not provided in example data
                    "aum": 0,  # Placeholder, not provided in example data
                    "tracking_error": 0,  # Placeholder
                    "sharpe_ratio": 0,  # Placeholder
                    "standard_deviation": 0,  # Placeholder
                    "exit_load": 0,  # Placeholder
                    "sector_allocation": {},  # Placeholder
                }
            else:
                print(
                    f"Error fetching data for scheme code {self.scheme_code}: {response.status_code}"
                )
                return {}
        except Exception as e:
            print(f"Error fetching data for scheme code {self.scheme_code}: {e}")
            return {}

    def assess_return(self, benchmark_return):
        """Evaluate how closely the fund's return matches or exceeds the benchmark."""
        return_score = 0
        fund_return = self.fund_data.get("annual_return", 0)
        difference = fund_return - benchmark_return
        if difference >= 0:
            return_score = 10
        elif difference > -1:
            return_score = 7
        else:
            return_score = 4
        return return_score

    def assess_expense_ratio(self):
        """Lower expense ratios are better for index funds."""
        expense_ratio = self.fund_data.get("expense_ratio", 0)
        if expense_ratio <= 0.2:
            return 10
        elif expense_ratio <= 0.5:
            return 7
        else:
            return 4

    def assess_tracking_error(self):
        """Lower tracking error indicates closer alignment with the benchmark."""
        tracking_error = self.fund_data.get("tracking_error", 0)
        if tracking_error <= 0.2:
            return 10
        elif tracking_error <= 0.5:
            return 7
        else:
            return 4

    def assess_risk(self):
        """Evaluate standard deviation and Sharpe ratio to assess risk-adjusted returns."""
        risk_score = 0
        standard_deviation = self.fund_data.get("standard_deviation", 0)
        sharpe_ratio = self.fund_data.get("sharpe_ratio", 0)

        if standard_deviation <= 10:
            risk_score += 5
        elif standard_deviation <= 20:
            risk_score += 3
        else:
            risk_score += 1

        if sharpe_ratio >= 1:
            risk_score += 5
        elif sharpe_ratio >= 0.5:
            risk_score += 3
        else:
            risk_score += 1

        return risk_score

    def assess_aum(self):
        """Larger AUM indicates better trust and scalability."""
        aum = self.fund_data.get("aum", 0)
        if aum >= 1000:
            return 10
        elif aum >= 500:
            return 7
        else:
            return 4

    def assess_exit_load(self):
        """Lower or no exit load is preferable."""
        exit_load = self.fund_data.get("exit_load", 0)
        if exit_load == 0:
            return 10
        elif exit_load <= 1:
            return 7
        else:
            return 4

    def assess_portfolio_diversification(self):
        """Simple assessment based on sector allocation."""
        sector_allocation = self.fund_data.get("sector_allocation", {})
        max_sector_allocation = max(
            [weight for weight in sector_allocation.values()], default=100
        )
        if max_sector_allocation <= 25:
            return 10
        elif max_sector_allocation <= 40:
            return 7
        else:
            return 4

    def calculate_overall_score(self, benchmark_return):
        scores = [
            self.assess_return(benchmark_return),
            self.assess_expense_ratio(),
            self.assess_tracking_error(),
            self.assess_risk(),
            self.assess_aum(),
            self.assess_exit_load(),
            self.assess_portfolio_diversification(),
        ]
        return np.mean(scores)

    def rate_fund(self, benchmark_return):
        """Rate the fund based on the overall score."""
        overall_score = self.calculate_overall_score(benchmark_return)
        if overall_score >= 9:
            return f"Scheme Code {self.scheme_code} is Excellent with a score of {overall_score:.2f}"
        elif overall_score >= 7:
            return f"Scheme Code {self.scheme_code} is Good with a score of {overall_score:.2f}"
        elif overall_score >= 5:
            return f"Scheme Code {self.scheme_code} is Average with a score of {overall_score:.2f}"
        else:
            return f"Scheme Code {self.scheme_code} is Poor with a score of {overall_score:.2f}"


# Example Usage
benchmark_return = 12.0  # Example benchmark return in %
fund = IndexFundRater(
    scheme_code="100012"
)  # Example scheme code for an Indian mutual fund
print(fund.rate_fund(benchmark_return))
