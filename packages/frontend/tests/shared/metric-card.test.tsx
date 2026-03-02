import { render, screen } from "@testing-library/react"
import { MetricCard } from "@/components/shared/metric-card"
import { describe, it, expect } from "vitest"

describe("MetricCard", () => {
    it("renders with title and value", () => {
        render(<MetricCard title="Test Title" value="$5,000" />)
        expect(screen.getByText("Test Title")).toBeInTheDocument()
        expect(screen.getByText("$5,000")).toBeInTheDocument()
    })

    it("shows up trend correctly", () => {
        render(<MetricCard title="Sales" value="100" change="+10%" trend="up" />)
        const changeBadge = screen.getByLabelText("up by +10%")
        expect(changeBadge).toBeInTheDocument()
        expect(changeBadge).toHaveClass("text-emerald-500")
    })

    it("shows down trend correctly", () => {
        render(<MetricCard title="Churn" value="5%" change="-2%" trend="down" />)
        const changeBadge = screen.getByLabelText("down by -2%")
        expect(changeBadge).toBeInTheDocument()
        expect(changeBadge).toHaveClass("text-red-500")
    })
})
