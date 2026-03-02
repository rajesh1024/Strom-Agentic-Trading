"use client"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { usePortfolioStore } from "@/store/portfolio-store"

interface OrderParams {
    symbol: string
    quantity: number
    side: "buy" | "sell"
    type: "equity" | "crypto"
}

export function useSubmitOrder() {
    const queryClient = useQueryClient()
    const addTransaction = usePortfolioStore(state => state.addTransaction)

    return useMutation({
        mutationFn: async (order: OrderParams) => {
            // Simulate network request
            await new Promise((resolve, reject) => {
                setTimeout(() => {
                    // Simulate random failure for testing revert
                    if (order.quantity < 0) return reject(new Error("Invalid quantity"))
                    resolve({ ...order, id: Date.now().toString(), status: "filled", price: 100, timestamp: Date.now() })
                }, 500)
            })
            return null
        },
        onMutate: async (newOrder) => {
            // Optimistic update
            await queryClient.cancelQueries({ queryKey: ["portfolio"] })

            const previousData = queryClient.getQueryData(["portfolio"])

            // Add optimistic transaction to store immediately
            const optimisticTx = {
                id: `opt-${Date.now()}`,
                symbol: newOrder.symbol,
                type: newOrder.type,
                side: newOrder.side,
                price: 0,
                quantity: newOrder.quantity,
                timestamp: Date.now(),
                status: "pending" as const
            }

            addTransaction(optimisticTx)

            return { previousData, optimisticTx }
        },
        onError: (err, newOrder, context) => {
            // Revert on fail
            if (context?.previousData) {
                queryClient.setQueryData(["portfolio"], context.previousData)
            }
            // Realistically we'd mark the specific optimistic transaction as failed in the store
        },
        onSettled: () => {
            // Invalidate to fetch fresh data
            queryClient.invalidateQueries({ queryKey: ["portfolio"] })
        }
    })
}
