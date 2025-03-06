"""
MonarchMoney Python SDK - A Python library for interacting with the Monarch Money API.
"""

import asyncio
import calendar
import getpass
import json
import os
import pickle
import time
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Union

import oathtool
from aiohttp import ClientSession, FormData
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode

AUTH_HEADER_KEY = "authorization"
CSRF_KEY = "csrftoken"
SESSION_DIR = ".mm"
SESSION_FILE = f"{SESSION_DIR}/mm_session.pickle"


class RequireMFAException(Exception):
    pass


class LoginFailedException(Exception):
    pass


class RequestFailedException(Exception):
    pass


class MonarchMoneyEndpoints(object):
    BASE_URL = "https://api.monarchmoney.com"

    @classmethod
    def getLoginEndpoint(cls) -> str:
        return cls.BASE_URL + "/auth/login/"

    @classmethod
    def getGraphQL(cls) -> str:
        return cls.BASE_URL + "/graphql"


class MonarchMoney(object):
    def __init__(
        self,
        session_file: str = SESSION_FILE,
        timeout: int = 10,
        token: Optional[str] = None,
    ) -> None:
        self._headers = {
            "Accept": "application/json",
            "Client-Platform": "web",
            "Content-Type": "application/json",
            "User-Agent": "MonarchMoneyAPI (https://github.com/hammem/monarchmoney)",
        }
        if token:
            self._headers["Authorization"] = f"Token {token}"

        self._session_file = session_file
        self._token = token
        self._timeout = timeout

    @property
    def timeout(self) -> int:
        """The timeout, in seconds, for GraphQL calls."""
        return self._timeout

    def set_timeout(self, timeout_secs: int) -> None:
        """Sets the default timeout on GraphQL API calls, in seconds."""
        self._timeout = timeout_secs

    @property
    def token(self) -> Optional[str]:
        return self._token

    def set_token(self, token: str) -> None:
        self._token = token

    def save_session(self, filename: Optional[str] = None) -> None:
        """
        Saves the auth token needed to access a Monarch Money account.
        """
        if filename is None:
            filename = self._session_file
        filename = os.path.abspath(filename)

        session_data = {"token": self._token}

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as fh:
            pickle.dump(session_data, fh)

    def load_session(self, filename: Optional[str] = None) -> None:
        """
        Loads pre-existing auth token from a Python pickle file.
        """
        if filename is None:
            filename = self._session_file

        with open(filename, "rb") as fh:
            data = pickle.load(fh)
            self.set_token(data["token"])
            self._headers["Authorization"] = f"Token {self._token}"

    def delete_session(self, filename: Optional[str] = None) -> None:
        """
        Deletes the session file.
        """
        if filename is None:
            filename = self._session_file

        if os.path.exists(filename):
            os.remove(filename)

    async def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        use_saved_session: bool = True,
        save_session: bool = True,
        mfa_secret_key: Optional[str] = None,
    ) -> None:
        """Logs into a Monarch Money account."""
        if use_saved_session and os.path.exists(self._session_file):
            print(f"Using saved session found at {self._session_file}")
            self.load_session(self._session_file)
            return

        if (email is None) or (password is None) or (email == "") or (password == ""):
            raise LoginFailedException(
                "Email and password are required to login when not using a saved session."
            )
        await self._login_user(email, password, mfa_secret_key)
        if save_session:
            self.save_session(self._session_file)

    async def interactive_login(
        self, use_saved_session: bool = True, save_session: bool = True
    ) -> None:
        """Performs an interactive login for iPython and similar environments."""
        email = input("Email: ")
        passwd = getpass.getpass("Password: ")
        try:
            await self.login(email, passwd, use_saved_session, save_session)
        except RequireMFAException:
            await self.multi_factor_authenticate(
                email, passwd, input("Two Factor Code: ")
            )
            if save_session:
                self.save_session(self._session_file)

    async def multi_factor_authenticate(
        self, email: str, password: str, code: str
    ) -> None:
        """Performs multi-factor authentication to access a Monarch Money account."""
        await self._multi_factor_authenticate(email, password, code)

    async def get_accounts(self) -> Dict[str, Any]:
        """Gets the list of accounts configured in the Monarch Money account."""
        query = gql(
            """
            query GetAccounts {
                accounts {
                    id
                    displayName
                    syncDisabled
                    deactivatedAt
                    isHidden
                    isAsset
                    mask
                    createdAt
                    updatedAt
                    displayLastUpdatedAt
                    currentBalance
                    displayBalance
                    includeInNetWorth
                    hideFromList
                    hideTransactionsFromReports
                    includeBalanceInNetWorth
                    includeInGoalBalance
                    dataProvider
                    dataProviderAccountId
                    isManual
                    transactionsCount
                    holdingsCount
                    manualInvestmentsTrackingMethod
                    order
                    logoUrl
                    type {
                        name
                        display
                        __typename
                    }
                    subtype {
                        name
                        display
                        __typename
                    }
                    credential {
                        id
                        updateRequired
                        disconnectedFromDataProviderAt
                        dataProvider
                        institution {
                            id
                            plaidInstitutionId
                            name
                            status
                            __typename
                        }
                        __typename
                    }
                    institution {
                        id
                        name
                        primaryColor
                        url
                        __typename
                    }
                    __typename
                }
            }
        """
        )
        return await self.gql_call(
            operation="GetAccounts",
            graphql_query=query,
        )

    async def get_transactions(
        self,
        limit: int = 100,
        offset: Optional[int] = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: str = "",
        category_ids: List[str] = [],
        account_ids: List[str] = [],
        tag_ids: List[str] = [],
    ) -> Dict[str, Any]:
        """
        Gets transaction data from the account.

        :param limit: the maximum number of transactions to download.
        :param offset: the number of transactions to skip before retrieving results.
        :param start_date: the earliest date to get transactions from, in "yyyy-mm-dd" format.
        :param end_date: the latest date to get transactions from, in "yyyy-mm-dd" format.
        :param search: a string to filter transactions. use empty string for all results.
        :param category_ids: a list of category ids to filter.
        :param account_ids: a list of account ids to filter.
        :param tag_ids: a list of tag ids to filter.
        """
        query = gql(
            """
            query GetTransactionsList($offset: Int, $limit: Int, $filters: TransactionFilterInput, $orderBy: TransactionOrdering) {
                allTransactions(filters: $filters) {
                    totalCount
                    results(offset: $offset, limit: $limit, orderBy: $orderBy) {
                        id
                        amount
                        pending
                        date
                        hideFromReports
                        plaidName
                        notes
                        isRecurring
                        reviewStatus
                        needsReview
                        attachments {
                            id
                            extension
                            filename
                            originalAssetUrl
                            publicId
                            sizeBytes
                            __typename
                        }
                        isSplitTransaction
                        createdAt
                        updatedAt
                        category {
                            id
                            name
                            __typename
                        }
                        merchant {
                            name
                            id
                            transactionsCount
                            __typename
                        }
                        account {
                            id
                            displayName
                            __typename
                        }
                        tags {
                            id
                            name
                            color
                            order
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }
        """
        )

        variables = {
            "offset": offset,
            "limit": limit,
            "orderBy": "date",
            "filters": {
                "search": search,
                "categories": category_ids,
                "accounts": account_ids,
                "tags": tag_ids,
            },
        }

        if start_date and end_date:
            variables["filters"]["startDate"] = start_date
            variables["filters"]["endDate"] = end_date
        elif bool(start_date) != bool(end_date):
            raise Exception(
                "You must specify both a startDate and endDate, not just one of them."
            )

        return await self.gql_call(
            operation="GetTransactionsList",
            graphql_query=query,
            variables=variables,
        )

    async def _login_user(
        self, email: str, password: str, mfa_secret_key: Optional[str]
    ) -> None:
        """Performs the initial login to a Monarch Money account."""
        data = {
            "password": password,
            "supports_mfa": True,
            "trusted_device": False,
            "username": email,
        }

        if mfa_secret_key:
            data["totp"] = oathtool.generate_otp(mfa_secret_key)

        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                MonarchMoneyEndpoints.getLoginEndpoint(), json=data
            ) as resp:
                if resp.status == 403:
                    raise RequireMFAException("Multi-Factor Auth Required")
                elif resp.status != 200:
                    raise LoginFailedException(
                        f"HTTP Code {resp.status}: {resp.reason}"
                    )

                response = await resp.json()
                self.set_token(response["token"])
                self._headers["Authorization"] = f"Token {self._token}"

    async def _multi_factor_authenticate(
        self, email: str, password: str, code: str
    ) -> None:
        """Performs the MFA step of login."""
        data = {
            "password": password,
            "supports_mfa": True,
            "totp": code,
            "trusted_device": False,
            "username": email,
        }

        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                MonarchMoneyEndpoints.getLoginEndpoint(), json=data
            ) as resp:
                if resp.status != 200:
                    try:
                        response = await resp.json()
                        if "detail" in response:
                            error_message = response["detail"]
                            raise RequireMFAException(error_message)
                        elif "error_code" in response:
                            error_message = response["error_code"]
                        else:
                            error_message = f"Unrecognized error message: '{response}'"
                        raise LoginFailedException(error_message)
                    except:
                        raise LoginFailedException(
                            f"HTTP Code {resp.status}: {resp.reason}\nRaw response: {resp.text}"
                        )
                response = await resp.json()
                self.set_token(response["token"])
                self._headers["Authorization"] = f"Token {self._token}"

    async def gql_call(
        self,
        operation: str,
        graphql_query: DocumentNode,
        variables: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """Makes a GraphQL call to Monarch Money's API."""
        return await self._get_graphql_client().execute_async(
            document=graphql_query,
            operation_name=operation,
            variable_values=variables,
        )

    def _get_graphql_client(self) -> Client:
        """Creates a correctly configured GraphQL client for connecting to Monarch Money."""
        if self._headers is None:
            raise LoginFailedException(
                "Make sure you call login() first or provide a session token!"
            )
        transport = AIOHTTPTransport(
            url=MonarchMoneyEndpoints.getGraphQL(),
            headers=self._headers,
            timeout=self._timeout,
        )
        return Client(
            transport=transport,
            fetch_schema_from_transport=False,
            execute_timeout=self._timeout,
        )