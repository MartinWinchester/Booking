# Code by https://github.com/jdrumgoole/pymongo-transactions/blob/6ea78c6a921bf2566b2c7b81f425391280c00707/transaction_retry.py#L12
import pymongo
class Transaction_Functor(object):
    '''
    Wrap a function so we can pass in a pymongo session object
    '''

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._session = None

    def __call__(self, session=None):
        if session is None:
            return self._func(*self._args, **self._kwargs)
        else:
            self._kwargs["session"] = session
            return self._func(*self._args, **self._kwargs)


def commit_with_retry(session):
    while True:
        try:
            # Commit uses write concern set at transaction start.
            session.commit_transaction()
            print("Transaction committed.")
            break
        except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
            # Can retry commit
            if exc.has_error_label("UnknownTransactionCommitResult"):
                print("UnknownTransactionCommitResult, retrying "
                      "commit operation ...")
                continue
            else:
                print("Error during commit ...")
                raise

def run_transaction_with_retry(functor, session):
    assert (isinstance(functor, Transaction_Functor))
    while True:
        try:
            with session.start_transaction():
                result=functor(session)  # performs transaction
                commit_with_retry(session)
            break
        except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
            # If transient error, retry the whole transaction
            if exc.has_error_label("TransientTransactionError"):
                print("TransientTransactionError, retrying "
                      "transaction ...")
                continue
            else:
                raise

    return result
