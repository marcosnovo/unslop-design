import SwiftUI

struct PaywallView: View {
    @State private var selected = 1
    @State private var secondsLeft = 599
    let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        ZStack {
            LinearGradient(colors: [.purple, .pink, .orange], startPoint: .topLeading, endPoint: .bottomTrailing).ignoresSafeArea()
            ScrollView {
                VStack(spacing: 18) {
                    Text("👑").font(.system(size: 64))
                    Text("Unlock Your Full Potential")
                        .font(.system(size: 32, weight: .black)).multilineTextAlignment(.center)
                    Text("Join 2,000,000+ happy users who transformed their lives!")
                        .font(.system(size: 15)).foregroundColor(.white.opacity(0.8))
                    Text("⏰ Offer ends in \(secondsLeft / 60):\(String(format: "%02d", secondsLeft % 60))")
                        .font(.system(size: 14, weight: .bold)).padding(10)
                        .background(Color.red).cornerRadius(20)
                    VStack(alignment: .leading, spacing: 12) {
                        Label("Unlimited Everything", systemImage: "checkmark.seal.fill")
                        Label("AI-Powered Insights", systemImage: "sparkles")
                        Label("Priority Support 24/7", systemImage: "bolt.fill")
                        Label("Exclusive Content", systemImage: "star.fill")
                    }.font(.system(size: 16, weight: .semibold))
                    PlanCard(title: "Weekly", price: "$9.99/week", badge: nil, isSelected: selected == 0).onTapGesture { selected = 0 }
                    PlanCard(title: "Yearly", price: "$59.99/year", badge: "SAVE 88% 🔥 MOST POPULAR", isSelected: selected == 1).onTapGesture { selected = 1 }
                    PlanCard(title: "Lifetime", price: "$149.99", badge: "BEST VALUE", isSelected: selected == 2).onTapGesture { selected = 2 }
                    Button(action: {}) {
                        Text("Start My Free Trial 🚀").font(.system(size: 18, weight: .heavy)).frame(maxWidth: .infinity).padding(18)
                            .background(Color.white).foregroundColor(.purple).cornerRadius(30)
                            .shadow(color: .pink.opacity(0.6), radius: 20)
                    }
                    Text("Cancel anytime. No commitment!").font(.system(size: 12)).foregroundColor(.white.opacity(0.6))
                }
                .padding(22).foregroundColor(.white)
            }
        }
        .onReceive(timer) { _ in secondsLeft = secondsLeft > 0 ? secondsLeft - 1 : 599 }
    }
}

struct PlanCard: View {
    let title: String; let price: String; let badge: String?; let isSelected: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let badge { Text(badge).font(.system(size: 11, weight: .black)).padding(.horizontal, 8).padding(.vertical, 4).background(Color.yellow).foregroundColor(.black).cornerRadius(8) }
            Text(title).font(.system(size: 18, weight: .bold))
            Text(price).font(.system(size: 15))
        }
        .frame(maxWidth: .infinity, alignment: .leading).padding(16)
        .background(Color.white.opacity(isSelected ? 0.3 : 0.12)).cornerRadius(18)
        .overlay(RoundedRectangle(cornerRadius: 18).stroke(isSelected ? Color.white : Color.clear, lineWidth: 2))
    }
}
