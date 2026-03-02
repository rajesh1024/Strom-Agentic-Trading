import { render, screen } from "@testing-library/react"
import { LoadingSpinner } from "@/components/shared/loading-spinner"
import { describe, it, expect } from "vitest"

describe("LoadingSpinner", () => {
    it("renders with a label", () => {
        render(<LoadingSpinner label="Fetching data..." />)
        const elements = screen.getAllByText("Fetching data...")
        expect(elements.length).toBeGreaterThan(0)
        expect(elements[0]).toBeInTheDocument()
    })

    it("has correctly set ARIA role and label", () => {
        render(<LoadingSpinner label="Loading" />)
        expect(screen.getByRole("status")).toHaveAttribute("aria-label", "Loading")
    })
})
