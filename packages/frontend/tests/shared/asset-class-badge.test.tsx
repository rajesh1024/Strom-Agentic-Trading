import { render, screen } from "@testing-library/react"
import { AssetClassBadge } from "@/components/shared/asset-class-badge"
import { describe, it, expect } from "vitest"

describe("AssetClassBadge", () => {
    it("renders the asset class text", () => {
        render(<AssetClassBadge assetClass="Equity" />)
        expect(screen.getByText("Equity")).toBeInTheDocument()
    })

    it("applies equity specific styling", () => {
        render(<AssetClassBadge assetClass="Equity" />)
        const badge = screen.getByText("Equity")
        expect(badge).toHaveClass("text-emerald-500")
    })

    it("applies crypto specific styling", () => {
        render(<AssetClassBadge assetClass="Crypto" />)
        const badge = screen.getByText("Crypto")
        expect(badge).toHaveClass("text-purple-500")
    })
})
