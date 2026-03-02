import { renderHook, act, waitFor } from "@testing-library/react"
import { useSubmitOrder } from "@/hooks/use-submit-order"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { usePortfolioStore } from "@/store/portfolio-store"
import { describe, it, expect, beforeEach } from "vitest"

const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
})

const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

describe("useSubmitOrder", () => {
    beforeEach(() => {
        queryClient.clear()
        usePortfolioStore.setState({ history: [], positions: [], balance: { total: 0, equity: 0, crypto: 0, cash: 0 } })
    })

    it("adds an optimistic transaction to the store", async () => {
        const { result } = renderHook(() => useSubmitOrder(), { wrapper })

        act(() => {
            result.current.mutate({ symbol: "AAPL", side: "buy", quantity: 10, type: "equity" })
        })

        await waitFor(() => {
            const history = usePortfolioStore.getState().history
            expect(history.length).toBe(1)
            expect(history[0].symbol).toBe("AAPL")
            expect(history[0].status).toBe("pending") // Optimistic state initially
        })
    })
})
