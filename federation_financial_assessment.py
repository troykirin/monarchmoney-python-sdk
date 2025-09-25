#!/usr/bin/env python3
"""
Federation financial assessment tool for Monarch Money.

This tool analyzes financial data across multiple accounts and institutions
to provide a comprehensive assessment of financial health and opportunities.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

from monarchmoney import MonarchMoney

class FederationAssessment:
    def __init__(self, token: str = None):
        """Initialize with optional token."""
        self.token = token or os.getenv('MONARCH_TOKEN')
        if not self.token:
            raise ValueError("Token required. Set MONARCH_TOKEN or provide token.")
        self.mm = MonarchMoney(token=self.token)

    async def analyze_accounts(self) -> Dict[str, Any]:
        """Analyze all accounts and their relationships."""
        accounts = await self.mm.get_accounts()
        account_list = accounts.get('accounts', [])

        # Group accounts by type
        account_types = {}
        for account in account_list:
            type_name = account.get('type', {}).get('name', 'unknown')
            if type_name not in account_types:
                account_types[type_name] = []
            account_types[type_name].append(account)

        # Calculate metrics
        metrics = {
            'total_accounts': len(account_list),
            'account_types': len(account_types),
            'total_assets': 0,
            'total_liabilities': 0,
            'account_distribution': {},
            'institution_distribution': {},
            'manual_accounts': 0,
            'synced_accounts': 0,
            'active_accounts': 0,
            'inactive_accounts': 0
        }

        institutions = {}

        for account in account_list:
            # Asset/liability tracking
            balance = account.get('currentBalance', 0) or 0
            if account.get('isAsset', True):
                metrics['total_assets'] += balance
            else:
                metrics['total_liabilities'] += abs(balance)

            # Account type distribution
            type_name = account.get('type', {}).get('display', 'Unknown')
            metrics['account_distribution'][type_name] = metrics['account_distribution'].get(type_name, 0) + 1

            # Institution tracking
            institution = account.get('institution', {}).get('name', 'Unknown')
            if institution not in institutions:
                institutions[institution] = {
                    'accounts': 0,
                    'total_balance': 0,
                    'asset_accounts': 0,
                    'liability_accounts': 0
                }
            institutions[institution]['accounts'] += 1
            institutions[institution]['total_balance'] += balance
            if account.get('isAsset', True):
                institutions[institution]['asset_accounts'] += 1
            else:
                institutions[institution]['liability_accounts'] += 1

            # Manual vs synced tracking
            if account.get('isManual', False):
                metrics['manual_accounts'] += 1
            else:
                metrics['synced_accounts'] += 1

            # Active vs inactive tracking
            if account.get('deactivatedAt'):
                metrics['inactive_accounts'] += 1
            else:
                metrics['active_accounts'] += 1

        metrics['institution_distribution'] = institutions
        metrics['net_worth'] = metrics['total_assets'] - metrics['total_liabilities']

        return metrics

    async def analyze_transactions(self, days: int = 30) -> Dict[str, Any]:
        """Analyze recent transactions across all accounts."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        transactions = await self.mm.get_transactions(
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

        transaction_list = transactions.get('allTransactions', {}).get('results', [])

        metrics = {
            'total_transactions': len(transaction_list),
            'total_inflow': 0,
            'total_outflow': 0,
            'categories': {},
            'merchants': {},
            'accounts': {},
            'daily_volume': {},
            'recurring_transactions': 0
        }

        for transaction in transaction_list:
            amount = transaction.get('amount', 0)

            # Track inflow/outflow
            if amount > 0:
                metrics['total_inflow'] += amount
            else:
                metrics['total_outflow'] += abs(amount)

            # Track categories
            category = transaction.get('category', {}).get('name', 'Uncategorized')
            if category not in metrics['categories']:
                metrics['categories'][category] = {
                    'count': 0,
                    'total': 0,
                    'average': 0
                }
            metrics['categories'][category]['count'] += 1
            metrics['categories'][category]['total'] += amount
            metrics['categories'][category]['average'] = (
                metrics['categories'][category]['total'] /
                metrics['categories'][category]['count']
            )

            # Track merchants
            merchant = transaction.get('merchant', {}).get('name', 'Unknown')
            if merchant not in metrics['merchants']:
                metrics['merchants'][merchant] = {
                    'count': 0,
                    'total': 0,
                    'average': 0
                }
            metrics['merchants'][merchant]['count'] += 1
            metrics['merchants'][merchant]['total'] += amount
            metrics['merchants'][merchant]['average'] = (
                metrics['merchants'][merchant]['total'] /
                metrics['merchants'][merchant]['count']
            )

            # Track accounts
            account = transaction.get('account', {}).get('displayName', 'Unknown')
            if account not in metrics['accounts']:
                metrics['accounts'][account] = {
                    'count': 0,
                    'total': 0,
                    'average': 0
                }
            metrics['accounts'][account]['count'] += 1
            metrics['accounts'][account]['total'] += amount
            metrics['accounts'][account]['average'] = (
                metrics['accounts'][account]['total'] /
                metrics['accounts'][account]['count']
            )

            # Track daily volume
            date = transaction.get('date', '')
            if date:
                if date not in metrics['daily_volume']:
                    metrics['daily_volume'][date] = {
                        'count': 0,
                        'total': 0
                    }
                metrics['daily_volume'][date]['count'] += 1
                metrics['daily_volume'][date]['total'] += abs(amount)

            # Track recurring transactions
            if transaction.get('isRecurring', False):
                metrics['recurring_transactions'] += 1

        # Calculate averages
        metrics['average_daily_transactions'] = metrics['total_transactions'] / days
        metrics['average_transaction_size'] = (
            (metrics['total_inflow'] + metrics['total_outflow']) /
            metrics['total_transactions'] if metrics['total_transactions'] > 0 else 0
        )

        # Sort and limit lists
        metrics['top_categories'] = sorted(
            metrics['categories'].items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )[:10]

        metrics['top_merchants'] = sorted(
            metrics['merchants'].items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )[:10]

        return metrics

    async def generate_assessment(self) -> Dict[str, Any]:
        """Generate comprehensive financial assessment."""
        print("\n🔄 Analyzing accounts...")
        account_metrics = await self.analyze_accounts()

        print("🔄 Analyzing transactions...")
        transaction_metrics = await self.analyze_transactions()

        assessment = {
            'timestamp': datetime.now().isoformat(),
            'account_metrics': account_metrics,
            'transaction_metrics': transaction_metrics,
            'insights': []
        }

        # Generate insights
        insights = []

        # Account insights
        if account_metrics['manual_accounts'] > account_metrics['synced_accounts']:
            insights.append({
                'type': 'warning',
                'message': 'High number of manual accounts may indicate opportunity for automation'
            })

        if account_metrics['inactive_accounts'] > 0:
            insights.append({
                'type': 'info',
                'message': f"Found {account_metrics['inactive_accounts']} inactive accounts that could be archived"
            })

        # Transaction insights
        recurring_ratio = (
            transaction_metrics['recurring_transactions'] /
            transaction_metrics['total_transactions']
            if transaction_metrics['total_transactions'] > 0 else 0
        )
        if recurring_ratio < 0.1:
            insights.append({
                'type': 'warning',
                'message': 'Low number of recurring transactions identified - may need review'
            })

        # Financial health insights
        if account_metrics['total_liabilities'] > 0:
            debt_ratio = account_metrics['total_liabilities'] / account_metrics['total_assets']
            if debt_ratio > 0.5:
                insights.append({
                    'type': 'warning',
                    'message': 'High debt-to-asset ratio detected'
                })

        assessment['insights'] = insights

        # Save assessment
        filename = f"data/federation_assessment/assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(assessment, f, indent=2)

        # Generate summary markdown
        summary_file = "federation_assessment/CURRENT_FINANCIAL_SUMMARY.md"
        os.makedirs(os.path.dirname(summary_file), exist_ok=True)
        with open(summary_file, 'w') as f:
            f.write("# Current Financial Summary\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Account Overview\n\n")
            f.write(f"- Total Accounts: {account_metrics['total_accounts']}\n")
            f.write(f"- Active Accounts: {account_metrics['active_accounts']}\n")
            f.write(f"- Total Assets: ${account_metrics['total_assets']:,.2f}\n")
            f.write(f"- Total Liabilities: ${account_metrics['total_liabilities']:,.2f}\n")
            f.write(f"- Net Worth: ${account_metrics['net_worth']:,.2f}\n\n")

            f.write("## Transaction Analysis\n\n")
            f.write(f"- Total Transactions: {transaction_metrics['total_transactions']}\n")
            f.write(f"- Total Inflow: ${transaction_metrics['total_inflow']:,.2f}\n")
            f.write(f"- Total Outflow: ${transaction_metrics['total_outflow']:,.2f}\n")
            f.write(f"- Average Daily Transactions: {transaction_metrics['average_daily_transactions']:.1f}\n")
            f.write(f"- Recurring Transactions: {transaction_metrics['recurring_transactions']}\n\n")

            f.write("## Insights\n\n")
            for insight in insights:
                f.write(f"- [{insight['type'].upper()}] {insight['message']}\n")

        print(f"\n✅ Assessment saved to {filename}")
        print(f"✅ Summary saved to {summary_file}")

        return assessment

async def main():
    """Main entry point."""
    try:
        assessment = FederationAssessment()
        await assessment.generate_assessment()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("- Token might be expired (try getting a fresh one)")
        print("- Network connection issues")
        print("- API changes")

if __name__ == "__main__":
    asyncio.run(main())
