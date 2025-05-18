from typing import Callable, Iterable, Iterator, Optional, Self

from src.contracts.contract import Contract, Symbol


ContractOrContracts = Contract | Iterable[Contract]


class Contracts:
    def __init__(
            self,
            contracts: Optional[ContractOrContracts] = None,
            should_contract_be_included: Callable[[Contract], bool] = lambda _: True,
    ):
        self.contracts: dict[Symbol, Contract] = {}
        self.should_contract_be_included = should_contract_be_included
        if contracts: self._extend(contracts)

    def __len__(self):
        return len(self.contracts)

    def __iter__(self) -> Iterator[Contract]:
        return iter(self.contracts.values())

    def __getitem__(self, symbols: Symbol | Iterable[Symbol]) -> Contract | Self:
        return (
            self.contracts[symbols]
            if isinstance(symbols, Symbol) else
            Contracts(self.contracts[x] for x in symbols)
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join([x.base_symbol for x in self])})'

    def get(self, symbol: Symbol, default=None) -> Optional[Contract]:
        return self.contracts.get(symbol, default)

    def get_symbols(self) -> set[Symbol]:
        return set(self.contracts.keys())

    def get_base_symbols(self) -> list[Symbol]:
        return [x.base_symbol for x in self.contracts.values()]

    def get_sorted_by_turnover(self, ascending=False) -> list[Contract]:
        return sorted(self.contracts.values(), key=lambda x: x.turnover, reverse=not ascending)

    def extend(self, contracts: ContractOrContracts) -> Self:
        return Contracts(self._extend(contracts))

    def remove(self, symbols: Symbol | Iterable[Symbol]):
        if isinstance(symbols, Contract): symbols = [symbols]
        for x in symbols: self.contracts.pop(x)

    def _extend(self, contracts: ContractOrContracts) -> list[Contract]:
        if isinstance(contracts, Contract): contracts = [contracts]
        included_contracts = [x for x in contracts if self.should_contract_be_included(x)]
        self.contracts |= {x.symbol: x for x in included_contracts}
        return included_contracts
