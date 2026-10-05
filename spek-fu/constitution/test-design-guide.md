# Test Design Guide
This file represents a guide consisting of rules and multiple examples of writing tests for software application.

## Example Project: SpendTracker

A personal finance application that integrates with the user's bank to automatically import transactions, categorize spending, and track budgets.

---

## Table of Contents

1. [Conventions](#conventions)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [E2E Tests](#e2e-tests)

---

## Conventions

Every test reads as a **human-readable narrative** following BDD structure:

- **Given** — establishes the world (state, data, configuration).
- **When** — the action under test.
- **Then** — the observable outcome, always including a `because` parameter that explains **why** this outcome is expected.

### Behavior-Driven Testing Focus (BDD)

System behavior SHOULD be specified in terms of observable outcomes.

Tests MUST focus on behavior (what) rather than implementation details (how).

Tests MUST be as readable as possible and optimized for human scanning.

Tests MUST:

- Use a clear Given/When/Then narrative structure to create a natural flow.

- Reflect the Given/When/Then story in test naming (human-language phrasing).

- Use helper methods / builders / fixtures to keep the scenario readable and reduce noise.

- Prefer intention-revealing names over terse or generic names.

> **Setup-action pattern**: When a `Given` helper requires non-trivial preconditions (e.g., creating an entity through the application before testing against it), it may internally call `When` or `Then` helpers to drive that setup. These internal calls MUST include a `because` that makes the setup intent clear. The outer test's `Given` name still describes the resulting state, not the setup mechanics.

Rationale: Tests are executable specifications; readability is a primary quality attribute.

### Parameterized & Narrative Test Design

Tests MUST be designed with maximum flexibility and reusability through parameterization, NOT hardcoding test values or data.

Test method names MUST be neutral with respect to parameters and test data; they SHOULD describe the behavior being tested, not the specific values used.

A single test case MUST support multiple parameter sets and configurations without duplication or creating separate test methods for each variation.

Tests MUST be written as human-readable narratives composed of well-named helper methods. Each helper method MUST:

- Represent a single, clear step in the test flow (Given/When/Then phases).

- Use intention-revealing names that precisely describe what behavior or system they simulate.

- Prioritize readability over brevity. The sequence of helper method calls MUST form a coherent narrative with minimal boilerplate or visual noise.

Rationale: Parameterized tests eliminate redundancy, reduce maintenance burden, and prevent test explosion. Narrative-driven design with helper methods makes tests self-documenting, easier to understand at a glance, and more resistant to breakage when implementation details change.

> **Exception — E2E tests**: E2E tests favour distinct, narrative user stories over parameterized variations. Parameterization in E2E tests is rare and should only be used when multiple user journeys genuinely share the same action sequence with differing data.

### Test-Driven Development (TDD)

Development MUST follow Red–Green–Refactor cycles.

The TDD workflow MUST explicitly include:

1. **Create empty shell class/interface**: Define the class signature, public interface, and any required namespaces. The implementation body MUST remain empty or contain only placeholder `throw NotImplementedException()` statements.

2. **Write failing tests**: Write tests that reference the shell class and define the expected behavior (Red phase).

3. **Implement minimal code**: Add only the minimal implementation necessary to make each test pass (Green phase).

4. **Refactor**: Improve code structure while preserving all passing tests (Refactor phase).

Functional code MUST be written only in response to failing tests.

Only the minimal code necessary to pass a test MUST be implemented.

Refactoring MUST preserve behavior and improve structure.


### Explicit Parameters

All test method calls — Given, When, **and** Then — pass their values as **explicit named parameters**. No magic numbers, no implicit defaults buried inside helpers. The reader sees every meaningful value directly in the test body.

### The `because` Parameter

Every `Then` helper and every shared assertion wrapper accepts a `string because` parameter. This short sentence of reasoning answers the question *"why should this be true?"* and is forwarded to the assertion framework so it appears in failure messages. This makes both the code and the test output self-documenting.

### ConfigureTests

Each test file MUST define a `ConfigureTests(...)` method with **named optional parameters** that centralise all setup. Individual `Given` helpers call `ConfigureTests` with only the parameters they care about — everything else falls back to sensible defaults.

### Base Classes

Each test type owns a **base class** that holds infrastructure shared across all tests of that type (mocks, clients, database seeding, browser drivers, etc.). Individual test files inherit from this base and add only the helpers specific to their scenarios.

---

## Unit Tests

Unit tests validate **a single piece of domain logic** in isolation. All external dependencies are substituted with test doubles. The language stays close to the domain — no HTTP, no databases, no UI.

### Base Class — `UnitTestBase`

```csharp
public abstract class UnitTestBase
{
    // Shared infrastructure for all unit tests
    protected Mock<IClock> ClockMock { get; private set; }

    protected DateTime FixedNow { get; private set; }

    protected UnitTestBase()
    {
        FixedNow = new DateTime(2026, 03, 01);
        ClockMock = new Mock<IClock>();
        ClockMock.Setup(c => c.UtcNow).Returns(FixedNow);
    }

    // --- Shared assertion wrappers with reasoning ---

    protected static void AssertAmountEquals(
        decimal expected,
        decimal actual,
        string because)
        => Assert.Equal(expected, actual, 0.001m, because);

    protected static void AssertCountEquals(
        int expected,
        int actual,
        string because)
        => Assert.Equal(expected, actual, because);

    protected static void AssertCollectionIsEmpty<T>(
        IEnumerable<T> collection,
        string because)
        => Assert.Empty(collection, because);

    protected static void AssertStateEquals<T>(
        T expected,
        T actual,
        string because) where T : struct
        => Assert.Equal(expected, actual, because);
}
```

---

### File: `TransactionCategorizationTests.cs`

```csharp
public class TransactionCategorizationTests : UnitTestBase
{
    // --- System under test & collaborators -----------------------------------
    private TransactionCategorizer _categorizer = null!;
    private List<CategoryRule> _rules = null!;
    private Transaction _transaction = null!;
    private CategoryResult _result = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public void GivenARuleMatchingTheMerchant_WhenATransactionIsCategorized_ThenItReceivesTheMatchedCategory()
    {
        GivenARuleMatchingTheMerchant(
            merchantName: "CoffeeHouse",
            keyword: "coffee",
            category: "Food & Drink");

        WhenTheTransactionIsCategorized();

        ThenTheCategoryIs(
            expected: "Food & Drink",
            because: "the merchant name contains the keyword 'coffee' which maps to Food & Drink");
    }

    [Fact]
    public void GivenNoRulesExist_WhenATransactionIsCategorized_ThenItIsFlaggedAsUncategorized()
    {
        GivenNoRulesExist();

        WhenTheTransactionIsCategorized();

        ThenTheCategoryIs(
            expected: "Uncategorized",
            because: "no categorization rules exist so the system cannot assign a category");
    }

    [Theory]
    [InlineData("SuperMart",    120.00, "supermart",  "Groceries")]
    [InlineData("ShellStation",  55.00, "shell",      "Transport")]
    [InlineData("Netflix",       15.99, "netflix",    "Entertainment")]
    public void GivenARuleForTheVendor_WhenTheTransactionIsCategorized_ThenItMatchesTheCorrectCategory(
        string merchant, decimal amount, string keyword, string expected)
    {
        GivenARuleForTheVendor(
            merchantName: merchant,
            amount: amount,
            keyword: keyword,
            category: expected);

        WhenTheTransactionIsCategorized();

        ThenTheCategoryIs(
            expected: expected,
            because: $"the rule keyword '{keyword}' matches merchant '{merchant}'");
    }

    // --- ConfigureTests ------------------------------------------------------
    private void ConfigureTests(
        string merchantName      = "CoffeeHouse",
        decimal amount           = 4.50m,
        string? matchingKeyword  = "coffee",
        string expectedCategory  = "Food & Drink",
        bool hasCustomRules      = true)
    {
        _rules = new List<CategoryRule>();

        if (hasCustomRules)
        {
            _rules.Add(new CategoryRule(matchingKeyword!, expectedCategory));
        }

        _transaction = new Transaction(merchantName, amount, FixedNow);
        _categorizer = new TransactionCategorizer(_rules);
    }

    // --- Given ---------------------------------------------------------------

    private void GivenARuleMatchingTheMerchant(
        string merchantName, string keyword, string category)
        => ConfigureTests(
            merchantName: merchantName,
            matchingKeyword: keyword,
            expectedCategory: category);

    private void GivenNoRulesExist()
        => ConfigureTests(hasCustomRules: false);

    private void GivenARuleForTheVendor(
        string merchantName, decimal amount, string keyword, string category)
        => ConfigureTests(
            merchantName: merchantName,
            amount: amount,
            matchingKeyword: keyword,
            expectedCategory: category);

    // --- When ----------------------------------------------------------------

    private void WhenTheTransactionIsCategorized()
        => _result = _categorizer.Categorize(_transaction);

    // --- Then ----------------------------------------------------------------

    private void ThenTheCategoryIs(string expected, string because)
        => Assert.Equal(expected, _result.CategoryName, because);
}
```

---

### File: `BudgetCalculationTests.cs`

```csharp
public class BudgetCalculationTests : UnitTestBase
{
    // --- System under test & collaborators -----------------------------------
    private BudgetCalculator _calculator = null!;
    private Budget _budget = null!;
    private List<Transaction> _transactions = null!;
    private BudgetStatus _status = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public void GivenSpendingIsWithinTheBudget_WhenTheBudgetIsEvaluated_ThenTheStatusIsOnTrack()
    {
        GivenSpendingIsWithinTheBudget(
            monthlyLimit: 500.00m,
            spent: new[] { 100.00m, 75.00m });

        WhenTheBudgetIsEvaluated();

        ThenTheStatusIs(
            expected: BudgetState.OnTrack,
            because: "total spending of 175.00 is well below the 500.00 limit");
        ThenTheRemainingAmountIs(
            expected: 325.00m,
            because: "500.00 limit minus 175.00 spent leaves 325.00 remaining");
    }

    [Fact]
    public void GivenSpendingExceedsTheBudget_WhenTheBudgetIsEvaluated_ThenTheStatusIsOverBudget()
    {
        GivenSpendingExceedsTheBudget(
            monthlyLimit: 200.00m,
            spent: new[] { 150.00m, 150.00m });

        WhenTheBudgetIsEvaluated();

        ThenTheStatusIs(
            expected: BudgetState.OverBudget,
            because: "total spending of 300.00 exceeds the 200.00 limit");
        ThenTheOverageAmountIs(
            expected: 100.00m,
            because: "300.00 spent minus 200.00 limit equals 100.00 overage");
    }

    [Fact]
    public void GivenSpendingIsNearTheLimit_WhenTheBudgetIsEvaluated_ThenTheStatusIsWarning()
    {
        GivenSpendingIsNearTheLimit(
            monthlyLimit: 500.00m,
            spent: new[] { 200.00m, 250.00m });

        WhenTheBudgetIsEvaluated();

        ThenTheStatusIs(
            expected: BudgetState.Warning,
            because: "total spending of 450.00 is within 90% of the 500.00 limit");
    }

    // --- Given ---------------------------------------------------------------

    private void GivenSpendingIsWithinTheBudget(decimal monthlyLimit, decimal[] spent)
        => ConfigureTests(monthlyLimit: monthlyLimit, transactionAmounts: spent);

    private void GivenSpendingExceedsTheBudget(decimal monthlyLimit, decimal[] spent)
        => ConfigureTests(monthlyLimit: monthlyLimit, transactionAmounts: spent);

    private void GivenSpendingIsNearTheLimit(decimal monthlyLimit, decimal[] spent)
        => ConfigureTests(monthlyLimit: monthlyLimit, transactionAmounts: spent);

    // --- When ----------------------------------------------------------------

    private void WhenTheBudgetIsEvaluated()
        => _status = _calculator.Evaluate(_budget, _transactions);

    // --- Then ----------------------------------------------------------------

    private void ThenTheStatusIs(BudgetState expected, string because)
        => AssertStateEquals(expected, _status.State, because);

    private void ThenTheRemainingAmountIs(decimal expected, string because)
        => AssertAmountEquals(expected, _status.Remaining, because);

    private void ThenTheOverageAmountIs(decimal expected, string because)
        => AssertAmountEquals(expected, _status.Overage, because);
}
```

---

### File: `MonthlyReportGenerationTests.cs`

```csharp
public class MonthlyReportGenerationTests : UnitTestBase
{
    // --- System under test & collaborators -----------------------------------
    private MonthlyReportGenerator _generator = null!;
    private List<Transaction> _transactions = null!;
    private MonthlyReport _report = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public void GivenTransactionsAcrossMultipleCategories_WhenTheReportIsGenerated_ThenEachCategoryHasASummary()
    {
        GivenTransactionsAcrossMultipleCategories(
            transactionCount: 5,
            totalSpent: 250.00m,
            categoryCount: 2);

        WhenTheReportIsGenerated();

        ThenTheReportContainsCategorySummaries(
            expected: 2,
            because: "the 5 transactions are spread across 2 categories so 2 summaries are expected");
        ThenTheTotalSpentEquals(
            expected: 250.00m,
            because: "all 5 transactions sum to 250.00");
    }

    [Fact]
    public void GivenNoTransactionsThisMonth_WhenTheReportIsGenerated_ThenTheReportIsEmpty()
    {
        GivenNoTransactionsThisMonth();

        WhenTheReportIsGenerated();

        ThenTheReportHasNoTransactions(
            because: "no transactions were recorded this month so the report should be empty");
        ThenTheTotalSpentEquals(
            expected: 0.00m,
            because: "zero transactions means zero spending");
    }

    [Theory]
    [InlineData(10,  1000.00,  3)]
    [InlineData(1,   50.00,    1)]
    [InlineData(25,  3200.00,  5)]
    public void GivenAnyNumberOfTransactions_WhenTheReportIsGenerated_ThenTheTotalsAreCorrect(
        int count, decimal total, int categories)
    {
        GivenTransactionsExist(
            transactionCount: count,
            totalSpent: total,
            categoryCount: categories);

        WhenTheReportIsGenerated();

        ThenTheReportContainsTransactions(
            expected: count,
            because: $"exactly {count} transactions were provided to the report generator");
        ThenTheTotalSpentEquals(
            expected: total,
            because: $"the sum of all {count} transactions equals {total}");
        ThenTheReportContainsCategorySummaries(
            expected: categories,
            because: $"transactions span {categories} distinct categories");
    }

    // --- ConfigureTests ------------------------------------------------------
    private void ConfigureTests(
        int transactionCount    = 5,
        decimal totalSpent      = 250.00m,
        int categoryCount       = 2)
    {
        _transactions = Enumerable.Range(1, transactionCount)
            .Select(i => new Transaction(
                $"Merchant_{i}",
                totalSpent / transactionCount,
                FixedNow,
                $"Category_{(i % categoryCount) + 1}"))
            .ToList();

        _generator = new MonthlyReportGenerator(ClockMock.Object);
    }

    // --- Given ---------------------------------------------------------------

    private void GivenTransactionsAcrossMultipleCategories(
        int transactionCount, decimal totalSpent, int categoryCount)
        => ConfigureTests(
            transactionCount: transactionCount,
            totalSpent: totalSpent,
            categoryCount: categoryCount);

    private void GivenNoTransactionsThisMonth()
        => ConfigureTests(transactionCount: 0, totalSpent: 0.00m, categoryCount: 0);

    private void GivenTransactionsExist(
        int transactionCount, decimal totalSpent, int categoryCount)
        => ConfigureTests(
            transactionCount: transactionCount,
            totalSpent: totalSpent,
            categoryCount: categoryCount);

    // --- When ----------------------------------------------------------------

    private void WhenTheReportIsGenerated()
        => _report = _generator.Generate(FixedNow.Year, FixedNow.Month, _transactions);

    // --- Then ----------------------------------------------------------------

    private void ThenTheReportContainsCategorySummaries(int expected, string because)
        => AssertCountEquals(expected, _report.CategorySummaries.Count, because);

    private void ThenTheTotalSpentEquals(decimal expected, string because)
        => AssertAmountEquals(expected, _report.TotalSpent, because);

    private void ThenTheReportHasNoTransactions(string because)
        => AssertCollectionIsEmpty(_report.Transactions, because);

    private void ThenTheReportContainsTransactions(int expected, string because)
        => AssertCountEquals(expected, _report.Transactions.Count, because);
}
```

---

## Integration Tests

Integration tests validate that **multiple components collaborate correctly** through real infrastructure (databases, HTTP clients, message queues). External third-party services (e.g., the bank API) remain stubbed at the network boundary, but internal persistence and wiring are real.

### Base Class — `IntegrationTestBase`

```csharp
public abstract class IntegrationTestBase : IAsyncLifetime
{
    // Shared infrastructure for all integration tests
    protected HttpClient ApiClient { get; private set; } = null!;
    protected SpendTrackerDbContext Db { get; private set; } = null!;
    protected WireMockServer BankApiStub { get; private set; } = null!;

    private WebApplicationFactory<Program> _factory = null!;

    public async Task InitializeAsync()
    {
        BankApiStub = WireMockServer.Start();

        _factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    services.ReplaceWithTestDatabase();
                    services.Configure<BankApiOptions>(
                        o => o.BaseUrl = BankApiStub.Url!);
                });
            });

        ApiClient = _factory.CreateClient();
        Db = _factory.Services.GetRequiredService<SpendTrackerDbContext>();

        await Db.Database.MigrateAsync();
    }

    public async Task DisposeAsync()
    {
        BankApiStub.Stop();
        await _factory.DisposeAsync();
    }

    // --- Shared seed helpers -------------------------------------------------

    protected async Task<Guid> SeedUser(
        string name = "TestUser",
        decimal startingBalance = 1000.00m)
    {
        var user = new User(name, startingBalance);
        Db.Users.Add(user);
        await Db.SaveChangesAsync();
        return user.Id;
    }

    // --- Shared stub helpers -------------------------------------------------

    protected void StubBankReturnsTransactions(params BankTransaction[] transactions)
    {
        BankApiStub
            .Given(Request.Create().WithPath("/transactions").UsingGet())
            .RespondWith(Response.Create()
                .WithStatusCode(200)
                .WithBodyAsJson(transactions));
    }

    protected void StubBankIsUnavailable()
    {
        BankApiStub
            .Given(Request.Create().WithPath("/transactions").UsingGet())
            .RespondWith(Response.Create().WithStatusCode(503));
    }

    // --- Shared assertion wrappers with reasoning ---

    protected static void AssertStatusCodeEquals(
        HttpStatusCode expected,
        HttpResponseMessage response,
        string because)
        => Assert.Equal(expected, response.StatusCode, because);

    protected static void AssertAmountEquals(
        decimal expected,
        decimal actual,
        string because)
        => Assert.Equal(expected, actual, 0.001m, because);

    protected static void AssertCountEquals(
        int expected,
        int actual,
        string because)
        => Assert.Equal(expected, actual, because);

    protected static void AssertExists(
        object? value,
        string because)
        => Assert.NotNull(value, because);

    protected static void AssertDoesNotExist(
        bool exists,
        string because)
        => Assert.False(exists, because);

    protected static void AssertStateEquals<T>(
        T expected,
        T actual,
        string because) where T : struct
        => Assert.Equal(expected, actual, because);
}
```

---

### File: `BankSyncImportTests.cs`

```csharp
public class BankSyncImportTests : IntegrationTestBase
{
    // --- State shared across steps -------------------------------------------
    private Guid _userId;
    private HttpResponseMessage _response = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public async Task GivenTheBankReturnsNewTransactions_WhenTheUserSyncs_ThenTransactionsAppearInTheDatabase()
    {
        await GivenTheBankReturnsNewTransactions(
            transactionCount: 2,
            userBalance: 1000.00m);

        await WhenTheUserSyncs();

        ThenTheSyncSucceeds(
            because: "the bank API returned valid data so the sync should complete");
        await ThenTheTransactionCountInTheDatabaseIs(
            expected: 2,
            because: "the bank returned exactly 2 new transactions to import");
    }

    [Fact]
    public async Task GivenTheBankIsUnavailable_WhenTheUserSyncs_ThenASyncFailureIsReturned()
    {
        await GivenTheBankIsUnavailable();

        await WhenTheUserSyncs();

        ThenTheSyncFails(
            because: "the bank API returned 503 so the sync cannot complete");
        await ThenTheTransactionCountInTheDatabaseIs(
            expected: 0,
            because: "no data could be fetched from the unavailable bank");
    }

    [Fact]
    public async Task GivenDuplicateTransactionsExist_WhenTheUserSyncsAgain_ThenDuplicatesAreSkipped()
    {
        await GivenDuplicateTransactionsExist(
            externalId: "txn-001",
            merchant: "CoffeeHouse",
            amount: 4.50m);

        await WhenTheUserSyncs();

        ThenTheSyncSucceeds(
            because: "the sync itself should succeed even when all transactions are duplicates");
        await ThenTheTransactionCountInTheDatabaseIs(
            expected: 1,
            because: "the duplicate transaction with externalId 'txn-001' already existed and should not be re-imported");
    }

    // --- ConfigureTests ------------------------------------------------------
    private async Task ConfigureTests(
        bool bankIsAvailable            = true,
        BankTransaction[]? bankData     = null,
        decimal userBalance             = 1000.00m)
    {
        _userId = await SeedUser(startingBalance: userBalance);

        if (bankIsAvailable)
        {
            bankData ??= new[]
            {
                new BankTransaction("CoffeeHouse", -4.50m, DateTime.UtcNow),
                new BankTransaction("SuperMart",   -62.30m, DateTime.UtcNow),
            };
            StubBankReturnsTransactions(bankData);
        }
        else
        {
            StubBankIsUnavailable();
        }
    }

    // --- Given ---------------------------------------------------------------

    private async Task GivenTheBankReturnsNewTransactions(
        int transactionCount, decimal userBalance)
    {
        var bankData = Enumerable.Range(1, transactionCount)
            .Select(i => new BankTransaction($"Merchant_{i}", -10.00m * i, DateTime.UtcNow))
            .ToArray();

        await ConfigureTests(
            bankIsAvailable: true,
            bankData: bankData,
            userBalance: userBalance);
    }

    private async Task GivenTheBankIsUnavailable()
        => await ConfigureTests(bankIsAvailable: false);

    private async Task GivenDuplicateTransactionsExist(
        string externalId, string merchant, decimal amount)
    {
        var duplicate = new BankTransaction(merchant, -amount, DateTime.UtcNow, externalId: externalId);

        await ConfigureTests(bankData: new[] { duplicate });

        // Pre-seed the same transaction so the sync should skip it
        Db.Transactions.Add(new Transaction(merchant, amount, DateTime.UtcNow, externalId, _userId));
        await Db.SaveChangesAsync();

        // Bank will return it again on the next sync
        StubBankReturnsTransactions(duplicate);
    }

    // --- When ----------------------------------------------------------------

    private async Task WhenTheUserSyncs()
        => _response = await ApiClient.PostAsync($"/api/users/{_userId}/sync", null);

    // --- Then ----------------------------------------------------------------

    private void ThenTheSyncSucceeds(string because)
        => AssertStatusCodeEquals(HttpStatusCode.OK, _response, because);

    private void ThenTheSyncFails(string because)
        => AssertStatusCodeEquals(HttpStatusCode.ServiceUnavailable, _response, because);

    private async Task ThenTheTransactionCountInTheDatabaseIs(int expected, string because)
    {
        var count = await Db.Transactions.CountAsync(t => t.UserId == _userId);
        AssertCountEquals(expected, count, because);
    }
}
```

---

### File: `BudgetAlertTests.cs`

```csharp
public class BudgetAlertTests : IntegrationTestBase
{
    // --- State shared across steps -------------------------------------------
    private Guid _userId;
    private HttpResponseMessage _response = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public async Task GivenTheUserIsNearBudgetLimit_WhenANewTransactionArrives_ThenAWarningAlertIsCreated()
    {
        await GivenTheUserIsNearBudgetLimit(
            budgetLimit: 200.00m,
            existingSpending: new[] { 80.00m, 60.00m },
            newTransactionAmount: 50.00m);

        await WhenANewTransactionArrives();

        ThenTheSyncSucceeds(
            because: "the bank returned valid transaction data");
        await ThenAnAlertExistsWithSeverity(
            expected: AlertSeverity.Warning,
            because: "total spending of 190.00 reaches 95% of the 200.00 budget limit");
    }

    [Fact]
    public async Task GivenTheUserIsWellUnderBudget_WhenANewTransactionArrives_ThenNoAlertIsCreated()
    {
        await GivenTheUserIsWellUnderBudget(
            budgetLimit: 1000.00m,
            existingSpending: new[] { 20.00m },
            newTransactionAmount: 15.00m);

        await WhenANewTransactionArrives();

        ThenTheSyncSucceeds(
            because: "the bank returned valid transaction data");
        await ThenNoAlertsExist(
            because: "total spending of 35.00 is far below the 1000.00 budget limit");
    }

    [Fact]
    public async Task GivenTheUserAlreadyExceededTheBudget_WhenANewTransactionArrives_ThenACriticalAlertIsCreated()
    {
        await GivenTheUserAlreadyExceededTheBudget(
            budgetLimit: 100.00m,
            existingSpending: new[] { 60.00m, 50.00m },
            newTransactionAmount: 30.00m);

        await WhenANewTransactionArrives();

        ThenTheSyncSucceeds(
            because: "the bank returned valid transaction data");
        await ThenAnAlertExistsWithSeverity(
            expected: AlertSeverity.Critical,
            because: "total spending of 140.00 exceeds the 100.00 budget limit by 40%");
    }

    // --- ConfigureTests ------------------------------------------------------
    private async Task ConfigureTests(
        decimal budgetLimit             = 200.00m,
        decimal[] existingSpending      = null!,
        string category                 = "Food & Drink",
        bool bankIsAvailable            = true,
        decimal newTransactionAmount    = 50.00m)
    {
        existingSpending ??= new[] { 80.00m, 60.00m };

        _userId = await SeedUser();

        Db.Budgets.Add(new Budget(category, budgetLimit, DateTime.UtcNow, _userId));
        foreach (var amount in existingSpending)
        {
            Db.Transactions.Add(
                new Transaction("Merchant", amount, DateTime.UtcNow, category, _userId));
        }
        await Db.SaveChangesAsync();

        if (bankIsAvailable)
        {
            StubBankReturnsTransactions(
                new BankTransaction("NewMerchant", -newTransactionAmount, DateTime.UtcNow));
        }
    }

    // --- Given ---------------------------------------------------------------

    private async Task GivenTheUserIsNearBudgetLimit(
        decimal budgetLimit, decimal[] existingSpending, decimal newTransactionAmount)
        => await ConfigureTests(
            budgetLimit: budgetLimit,
            existingSpending: existingSpending,
            newTransactionAmount: newTransactionAmount);

    private async Task GivenTheUserIsWellUnderBudget(
        decimal budgetLimit, decimal[] existingSpending, decimal newTransactionAmount)
        => await ConfigureTests(
            budgetLimit: budgetLimit,
            existingSpending: existingSpending,
            newTransactionAmount: newTransactionAmount);

    private async Task GivenTheUserAlreadyExceededTheBudget(
        decimal budgetLimit, decimal[] existingSpending, decimal newTransactionAmount)
        => await ConfigureTests(
            budgetLimit: budgetLimit,
            existingSpending: existingSpending,
            newTransactionAmount: newTransactionAmount);

    // --- When ----------------------------------------------------------------

    private async Task WhenANewTransactionArrives()
        => _response = await ApiClient.PostAsync($"/api/users/{_userId}/sync", null);

    // --- Then ----------------------------------------------------------------

    private void ThenTheSyncSucceeds(string because)
        => AssertStatusCodeEquals(HttpStatusCode.OK, _response, because);

    private async Task ThenAnAlertExistsWithSeverity(AlertSeverity expected, string because)
    {
        var alert = await Db.Alerts.FirstOrDefaultAsync(a => a.UserId == _userId);
        AssertExists(alert, because: "an alert should have been created for this budget breach");
        AssertStateEquals(expected, alert!.Severity, because);
    }

    private async Task ThenNoAlertsExist(string because)
    {
        var exists = await Db.Alerts.AnyAsync(a => a.UserId == _userId);
        AssertDoesNotExist(exists, because);
    }
}
```

---

### File: `SpendingSummaryApiTests.cs`

```csharp
public class SpendingSummaryApiTests : IntegrationTestBase
{
    // --- State shared across steps -------------------------------------------
    private Guid _userId;
    private HttpResponseMessage _response = null!;
    private SpendingSummaryDto _summary = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public async Task GivenTheUserHasTransactions_WhenTheSummaryIsRequested_ThenItReturnsCorrectTotals()
    {
        await GivenTheUserHasTransactions(
            transactionCount: 3,
            amountPerTransaction: 40.00m);

        await WhenTheSummaryIsRequested();

        ThenTheResponseIsSuccessful(
            because: "the user exists and has transactions so the API should return 200");
        ThenTheTotalSpentIs(
            expected: 120.00m,
            because: "3 transactions at 40.00 each sum to 120.00");
        ThenTheTransactionCountIs(
            expected: 3,
            because: "exactly 3 transactions were seeded for this user");
    }

    [Fact]
    public async Task GivenTheUserHasNoTransactions_WhenTheSummaryIsRequested_ThenItReturnsZeros()
    {
        await GivenTheUserHasNoTransactions();

        await WhenTheSummaryIsRequested();

        ThenTheResponseIsSuccessful(
            because: "the endpoint should return 200 even with zero transactions");
        ThenTheTotalSpentIs(
            expected: 0.00m,
            because: "no transactions exist so the total must be zero");
        ThenTheTransactionCountIs(
            expected: 0,
            because: "no transactions were created for this user");
    }

    [Theory]
    [InlineData(10, 25.00,  250.00)]
    [InlineData(1,  99.99,  99.99)]
    [InlineData(50, 10.00,  500.00)]
    public async Task GivenVariousSpendingPatterns_WhenTheSummaryIsRequested_ThenTheTotalsMatchExpected(
        int count, decimal each, decimal expectedTotal)
    {
        await GivenTheUserHasTransactions(
            transactionCount: count,
            amountPerTransaction: each);

        await WhenTheSummaryIsRequested();

        ThenTheResponseIsSuccessful(
            because: "the user exists and the API should always return 200");
        ThenTheTotalSpentIs(
            expected: expectedTotal,
            because: $"{count} transactions at {each} each should sum to {expectedTotal}");
        ThenTheTransactionCountIs(
            expected: count,
            because: $"exactly {count} transactions were seeded");
    }

    // --- ConfigureTests ------------------------------------------------------
    private async Task ConfigureTests(
        int transactionCount         = 3,
        string category              = "Groceries",
        decimal amountPerTransaction = 40.00m)
    {
        _userId = await SeedUser();

        for (var i = 0; i < transactionCount; i++)
        {
            Db.Transactions.Add(
                new Transaction($"Store_{i}", amountPerTransaction, DateTime.UtcNow, category, _userId));
        }
        await Db.SaveChangesAsync();
    }

    // --- Given ---------------------------------------------------------------

    private async Task GivenTheUserHasTransactions(
        int transactionCount, decimal amountPerTransaction)
        => await ConfigureTests(
            transactionCount: transactionCount,
            amountPerTransaction: amountPerTransaction);

    private async Task GivenTheUserHasNoTransactions()
        => await ConfigureTests(transactionCount: 0);

    // --- When ----------------------------------------------------------------

    private async Task WhenTheSummaryIsRequested()
    {
        _response = await ApiClient.GetAsync($"/api/users/{_userId}/spending/summary");
        if (_response.IsSuccessStatusCode)
        {
            _summary = await _response.Content.ReadFromJsonAsync<SpendingSummaryDto>()
                       ?? new SpendingSummaryDto();
        }
    }

    // --- Then ----------------------------------------------------------------

    private void ThenTheResponseIsSuccessful(string because)
        => AssertStatusCodeEquals(HttpStatusCode.OK, _response, because);

    private void ThenTheTotalSpentIs(decimal expected, string because)
        => AssertAmountEquals(expected, _summary.TotalSpent, because);

    private void ThenTheTransactionCountIs(int expected, string because)
        => AssertCountEquals(expected, _summary.TransactionCount, because);
}
```

---

## E2E Tests

E2E tests validate **complete user journeys** through the real application, driven by a browser. They read almost entirely in user language — clicks, navigation, visible text. Technical setup is minimal and hidden in the base class.

### Base Class — `E2ETestBase`

```csharp
public abstract class E2ETestBase : IAsyncLifetime
{
    // Shared infrastructure for all E2E tests
    protected IPage Page { get; private set; } = null!;

    private IBrowser _browser = null!;
    private IBrowserContext _context = null!;

    public async Task InitializeAsync()
    {
        var playwright = await Playwright.CreateAsync();
        _browser = await playwright.Chromium.LaunchAsync(new() { Headless = true });
        _context = await _browser.NewContextAsync();
        Page = await _context.NewPageAsync();
    }

    public async Task DisposeAsync()
    {
        await _context.DisposeAsync();
        await _browser.DisposeAsync();
    }

    // --- Shared navigation & interaction helpers ---

    protected async Task NavigateTo(string path)
        => await Page.GotoAsync($"{TestEnvironment.BaseUrl}{path}");

    protected async Task ClickButton(string text)
        => await Page.GetByRole(AriaRole.Button, new() { Name = text }).ClickAsync();

    protected async Task FillField(string label, string value)
        => await Page.GetByLabel(label).FillAsync(value);

    protected async Task SelectFromDropdown(string label, string option)
        => await Page.GetByLabel(label).SelectOptionAsync(option);

    // --- Shared assertion wrappers with reasoning ---

    protected async Task AssertTextIsVisible(string text, string because)
    {
        var locator = Page.GetByText(text);
        await Expect(locator).ToBeVisibleAsync(new() { Message = because });
    }

    protected async Task AssertTextIsNotVisible(string text, string because)
    {
        var locator = Page.GetByText(text);
        await Expect(locator).Not.ToBeVisibleAsync(new() { Message = because });
    }

    protected async Task AssertElementIsVisible(string testId, string because)
    {
        var locator = Page.Locator($"[data-testid='{testId}']");
        await Expect(locator).ToBeVisibleAsync(new() { Message = because });
    }

    protected async Task AssertElementIsNotVisible(string testId, string because)
    {
        var locator = Page.Locator($"[data-testid='{testId}']");
        await Expect(locator).Not.ToBeVisibleAsync(new() { Message = because });
    }

    protected async Task AssertElementCount(
        string testId, int expected, string because)
    {
        var locator = Page.Locator($"[data-testid='{testId}']");
        await Expect(locator).ToHaveCountAsync(expected, new() { Message = because });
    }
}
```

---

### File: `UserCreatesBudgetTests.cs`

```csharp
public class UserCreatesBudgetTests : E2ETestBase
{
    // --- State ---------------------------------------------------------------
    private string _categoryName = null!;
    private string _budgetAmount = null!;

    // --- Tests ---------------------------------------------------------------

    [Fact]
    public async Task GivenTheUserIsLoggedIn_WhenTheyCreateABudget_ThenTheBudgetAppearsOnTheDashboard()
    {
        await GivenTheUserIsLoggedIn(
            category: "Groceries",
            amount: "300");

        await WhenTheyNavigateToTheBudgetPage();
        await WhenTheyCreateANewBudget(
            category: "Groceries",
            amount: "300");

        await ThenTheBudgetAppearsOnTheDashboard(
            expectedLabel: "Groceries — $300/mo",
            because: "the newly created budget should be immediately visible on the dashboard");
    }

    [Fact]
    public async Task GivenTheUserIsLoggedIn_WhenTheyCreateABudgetWithZeroAmount_ThenAValidationErrorIsShown()
    {
        await GivenTheUserIsLoggedIn(
            category: "Groceries",
            amount: "0");

        await WhenTheyNavigateToTheBudgetPage();
        await WhenTheyCreateANewBudget(
            category: "Groceries",
            amount: "0");

        await ThenAValidationErrorIsShown(
            expectedMessage: "Budget amount must be greater than zero",
            because: "zero is not a valid budget amount and the form should reject it");
    }

    [Fact]
    public async Task GivenABudgetAlreadyExists_WhenTheyCreateADuplicateForTheSameCategory_ThenADuplicateWarningIsShown()
    {
        await GivenABudgetAlreadyExistsForCategory(
            category: "Groceries",
            amount: "300");

        await WhenTheyNavigateToTheBudgetPage();
        await WhenTheyCreateANewBudget(
            category: "Groceries",
            amount: "500");

        await ThenADuplicateWarningIsShown(
            category: "Groceries",
            because: "only one budget per category is allowed and Groceries already has one");
    }

    // --- ConfigureTests ------------------------------------------------------
    private async Task ConfigureTests(
        string email        = "jane@example.com",
        string password     = "Test123!",
        string category     = "Groceries",
        string amount       = "300")
    {
        _categoryName = category;
        _budgetAmount = amount;

        await NavigateTo("/login");
        await FillField("Email", email);
        await FillField("Password", password);
        await ClickButton("Sign in");
    }

    // --- Given ---------------------------------------------------------------

    private async Task GivenTheUserIsLoggedIn(string category, string amount)
        => await ConfigureTests(category: category, amount: amount);

    private async Task GivenABudgetAlreadyExistsForCategory(string category, string amount)
    {
        await ConfigureTests(category: category, amount: amount);

        // Create the first budget so the second one is a duplicate
        await WhenTheyNavigateToTheBudgetPage();
        await WhenTheyCreateANewBudget(category: category, amount: amount);
        await ThenTheBudgetAppearsOnTheDashboard(
            expectedLabel: $"{category} — ${amount}/mo",
            because: "the initial budget must be created before testing duplicate detection");
    }

    // --- When ----------------------------------------------------------------

    private async Task WhenTheyNavigateToTheBudgetPage()
        => await NavigateTo("/budgets");

    private async Task WhenTheyCreateANewBudget(string category, string amount)
    {
        await ClickButton("New Budget");
        await SelectFromDropdown("Category", category);
        await FillField("Monthly Limit", amount);
        await ClickButton("Save");
    }

    // --- Then ----------------------------------------------------------------

    private async Task ThenTheBudgetAppearsOnTheDashboard(string expectedLabel, string because)
    {
        await NavigateTo("/dashboard");
        await AssertTextIsVisible(expectedLabel, because);
    }

    private async Task ThenAValidationErrorIsShown(string expectedMessage, string because)
        => await AssertTextIsVisible(expectedMessage, because);

    private async Task ThenADuplicateWarningIsShown(string category, string because)
        => await AssertTextIsVisible(
            text: $"A budget for {category} already exists",
            because: because);
}
```

---

### File: `UserReviewsSpendingHistoryTests.cs`

```csharp
public class UserReviewsSpendingHistoryTests : E2ETestBase
{
    // --- Tests ---------------------------------------------------------------

    [Fact]
    public async Task GivenTheUserHasSyncedTransactions_WhenTheyOpenSpendingHistory_ThenTransactionsAreVisible()
    {
        await GivenTheUserHasSyncedTransactions();

        await WhenTheyOpenSpendingHistory();

        await ThenTheTransactionListIsVisible(
            because: "the user synced transactions from the bank so the list should be populated");
        await ThenTheTransactionListHasRows(
            because: "at least one transaction row should appear after a successful sync");
    }

    [Fact]
    public async Task GivenTheUserHasNoTransactions_WhenTheyOpenSpendingHistory_ThenAnEmptyStateIsShown()
    {
        await GivenTheUserHasNoTransactions();

        await WhenTheyOpenSpendingHistory();

        await ThenAnEmptyStateMessageIsShown(
            expectedMessage: "No transactions yet. Sync with your bank to get started.",
            because: "the user never synced so there is no data to display");
    }

    [Fact]
    public async Task GivenTheUserHasTransactions_WhenTheyFilterByCategory_ThenOnlyMatchingTransactionsAppear()
    {
        await GivenTheUserHasSyncedTransactions();

        await WhenTheyOpenSpendingHistory();
        await WhenTheyFilterByCategory(category: "Groceries");

        await ThenCategoryIsVisible(
            category: "Groceries",
            because: "the filter is set to Groceries so those transactions should remain");
        await ThenCategoryIsHidden(
            category: "Entertainment",
            because: "the filter excludes Entertainment so those transactions should disappear");
    }

    // --- ConfigureTests ------------------------------------------------------
    private async Task ConfigureTests(
        string email         = "jane@example.com",
        string password      = "Test123!",
        bool hasTransactions = true)
    {
        await NavigateTo("/login");
        await FillField("Email", email);
        await FillField("Password", password);
        await ClickButton("Sign in");

        if (hasTransactions)
        {
            await NavigateTo("/dashboard");
            await ClickButton("Sync with Bank");
            await AssertTextIsVisible(
                text: "Sync complete",
                because: "the sync must succeed before testing spending history");
        }
    }

    // --- Given ---------------------------------------------------------------

    private async Task GivenTheUserHasSyncedTransactions()
        => await ConfigureTests(hasTransactions: true);

    private async Task GivenTheUserHasNoTransactions()
        => await ConfigureTests(hasTransactions: false);

    // --- When ----------------------------------------------------------------

    private async Task WhenTheyOpenSpendingHistory()
        => await NavigateTo("/spending/history");

    private async Task WhenTheyFilterByCategory(string category)
        => await SelectFromDropdown("Filter by Category", category);

    // --- Then ----------------------------------------------------------------

    private async Task ThenTheTransactionListIsVisible(string because)
        => await AssertElementIsVisible(testId: "transaction-list", because: because);

    private async Task ThenTheTransactionListHasRows(string because)
    {
        var rows = Page.Locator("[data-testid='transaction-row']");
        var count = await rows.CountAsync();
        Assert.True(count > 0, because);
    }

    private async Task ThenAnEmptyStateMessageIsShown(string expectedMessage, string because)
        => await AssertTextIsVisible(text: expectedMessage, because: because);

    private async Task ThenCategoryIsVisible(string category, string because)
        => await AssertTextIsVisible(text: category, because: because);

    private async Task ThenCategoryIsHidden(string category, string because)
        => await AssertTextIsNotVisible(text: category, because: because);
}
```

---

### File: `UserConnectsBankAccountTests.cs`

```csharp
public class UserConnectsBankAccountTests : E2ETestBase
{
    // --- Tests ---------------------------------------------------------------

    [Fact]
    public async Task GivenTheUserHasNoBankConnected_WhenTheyConnectTheirBank_ThenTheDashboardShowsTheAccountBalance()
    {
        await GivenTheUserHasNoBankConnected();

        await WhenTheyNavigateToSettings();
        await WhenTheyConnectTheirBank(
            bankUsername: "jane_bank",
            bankPassword: "secure_pass");
        await ThenTheConnectionIsConfirmed(
            because: "the bank credentials were valid so the connection should succeed");

        await WhenTheyReturnToTheDashboard();
        await ThenTheDashboardShowsTheAccountBalance(
            because: "a connected bank account should populate the balance widget on the dashboard");
    }

    [Fact]
    public async Task GivenTheUserHasNoBankConnected_WhenTheyDismissTheBankLoginDialog_ThenNoConnectionIsMade()
    {
        await GivenTheUserHasNoBankConnected();

        await WhenTheyNavigateToSettings();
        await WhenTheyStartAndCancelBankConnection();

        await ThenNoBankAccountIsConnected(
            because: "the user cancelled the bank login dialog so no connection should be established");
    }

    [Fact]
    public async Task GivenTheUserHasAnExistingBankConnection_WhenTheyDisconnect_ThenTheConnectionIsRemoved()
    {
        await GivenTheUserHasAnExistingBankConnection(
            bankUsername: "jane_bank",
            bankPassword: "secure_pass");

        await WhenTheyNavigateToSettings();
        await WhenTheyDisconnectTheirBank();

        await ThenNoBankAccountIsConnected(
            because: "the user explicitly disconnected so the connection should be removed");
        await WhenTheyReturnToTheDashboard();
        await ThenTheDashboardDoesNotShowAccountBalance(
            because: "without a connected bank the balance widget should not be visible");
    }

    // --- ConfigureTests ------------------------------------------------------
    private async Task ConfigureTests(
        string email    = "jane@example.com",
        string password = "Test123!")
    {
        await NavigateTo("/login");
        await FillField("Email", email);
        await FillField("Password", password);
        await ClickButton("Sign in");
    }

    // --- Given ---------------------------------------------------------------

    private async Task GivenTheUserHasNoBankConnected()
        => await ConfigureTests();

    private async Task GivenTheUserHasAnExistingBankConnection(
        string bankUsername, string bankPassword)
    {
        await ConfigureTests();

        await WhenTheyNavigateToSettings();
        await WhenTheyConnectTheirBank(
            bankUsername: bankUsername,
            bankPassword: bankPassword);
        await ThenTheConnectionIsConfirmed(
            because: "the initial connection must succeed before testing disconnection");
    }

    // --- When ----------------------------------------------------------------

    private async Task WhenTheyNavigateToSettings()
        => await NavigateTo("/settings");

    private async Task WhenTheyConnectTheirBank(string bankUsername, string bankPassword)
    {
        await ClickButton("Connect Bank Account");
        await FillField("Bank Username", bankUsername);
        await FillField("Bank Password", bankPassword);
        await ClickButton("Authorize");
    }

    private async Task WhenTheyStartAndCancelBankConnection()
    {
        await ClickButton("Connect Bank Account");
        await ClickButton("Cancel");
    }

    private async Task WhenTheyDisconnectTheirBank()
    {
        await ClickButton("Disconnect");
        await ClickButton("Confirm");
    }

    private async Task WhenTheyReturnToTheDashboard()
        => await NavigateTo("/dashboard");

    // --- Then ----------------------------------------------------------------

    private async Task ThenTheConnectionIsConfirmed(string because)
        => await AssertTextIsVisible(
            text: "Bank account connected successfully",
            because: because);

    private async Task ThenNoBankAccountIsConnected(string because)
        => await AssertTextIsVisible(
            text: "No bank account connected",
            because: because);

    private async Task ThenTheDashboardShowsTheAccountBalance(string because)
        => await AssertElementIsVisible(testId: "account-balance", because: because);

    private async Task ThenTheDashboardDoesNotShowAccountBalance(string because)
        => await AssertElementIsNotVisible(testId: "account-balance", because: because);
}
```

---

## Quick Reference

| Aspect | Unit | Integration | E2E |
|---|---|---|---|
| **Base class** | `UnitTestBase` | `IntegrationTestBase` | `E2ETestBase` |
| **Infrastructure** | Mocks, stubs, in-memory | Real DB, HTTP client, WireMock stubs | Real browser via Playwright |
| **Language** | Domain logic | API calls + DB verification | User actions + visible outcomes |
| **ConfigureTests** | Sets up domain objects, rules, mocks | Seeds DB, configures stubs | Logs in, navigates, sets UI state |
| **When helpers** | Call domain methods directly | Call API endpoints | Click, type, navigate |
| **Then helpers** | Assert return values with `because` | Assert DB state + HTTP status with `because` | Assert visible text + page state with `because` |
| **Assertion wrappers** | `AssertAmountEquals`, `AssertStateEquals`, `AssertCountEquals`, `AssertCollectionIsEmpty` | Redefines unit wrappers (`AssertAmountEquals`, `AssertCountEquals`, `AssertStateEquals`) + `AssertStatusCodeEquals`, `AssertExists`, `AssertDoesNotExist` | `AssertTextIsVisible`, `AssertTextIsNotVisible`, `AssertElementIsVisible`, `AssertElementCount` |
| **Parameterization** | `[Theory]` + `[InlineData]` | `[Theory]` + `[InlineData]` | Rare — E2E tests favour distinct user stories |
| **Explicit params** | All Given/When/Then calls use named parameters | All Given/When/Then calls use named parameters | All Given/When/Then calls use named parameters |
| **`because` reasoning** | On every `Then` + every base assertion | On every `Then` + every base assertion | On every `Then` + every base assertion |
