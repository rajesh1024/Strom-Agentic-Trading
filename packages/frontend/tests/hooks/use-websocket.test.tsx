import { renderHook, act } from "@testing-library/react"
import { useWebSocket } from "@/hooks/use-websocket"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { useSignalStore } from "@/store/signal-store"
import { useAgentStore } from "@/store/agent-store"

const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
})

const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

describe("useWebSocket", () => {
    beforeEach(() => {
        queryClient.clear()
        useSignalStore.setState({ signals: [], unreadCount: 0 })
        useAgentStore.setState({ agents: {} })
    })

    it("sets connection status to true on mount", () => {
        const { result } = renderHook(() => useWebSocket(), { wrapper })
        expect(result.current.isConnected).toBe(true)
    })

    it("handles portfolio_update by invalidating queries", () => {
        const spy = vi.spyOn(queryClient, "invalidateQueries")
        const { result } = renderHook(() => useWebSocket(), { wrapper })

        act(() => {
            result.current.processMessage({ type: "portfolio_update", data: {} })
        })

        expect(spy).toHaveBeenCalledWith({ queryKey: ["portfolio"] })
    })

    it("handles signal_received by updating the signal store", () => {
        const { result } = renderHook(() => useWebSocket(), { wrapper })

        act(() => {
            result.current.processMessage({
                type: "signal_received",
                data: {
                    id: "1",
                    symbol: "AAPL",
                    action: "buy",
                    level: "info",
                    message: "Buy signal",
                    confidence: 0.9,
                    timestamp: Date.now(),
                },
            })
        })

        const signals = useSignalStore.getState().signals
        expect(signals).toHaveLength(1)
        expect(signals[0].symbol).toBe("AAPL")
    })
})
