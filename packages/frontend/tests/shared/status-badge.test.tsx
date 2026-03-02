import { render, screen } from "@testing-library/react"
import { StatusBadge } from "@/components/shared/status-badge"
import { describe, it, expect } from "vitest"

describe("StatusBadge", () => {
    it("renders with the status label", () => {
        render(<StatusBadge status="success" label="Completed" />)
        expect(screen.getByText("Completed")).toBeInTheDocument()
    })

    it("shows the status dot by default", () => {
        render(<StatusBadge status="error" />)
        const dot = screen.getByTestId("status-dot")
        expect(dot).toBeInTheDocument()
        expect(dot).toHaveClass("bg-red-500")
    })

    it("can hide the dot", () => {
        render(<StatusBadge status="info" dot={false} />)
        const dot = screen.queryByTestId("status-dot")
        expect(dot).not.toBeInTheDocument()
    })
})
