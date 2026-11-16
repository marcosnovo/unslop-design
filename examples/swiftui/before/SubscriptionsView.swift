import SwiftUI

struct SubscriptionsView: View {
    let subs = Subscription.samples
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Text("Hey Maya! 👋")
                        .font(.system(size: 15))
                        .foregroundColor(.secondary)
                    Text("Your Subscriptions")
                        .font(.system(size: 30, weight: .heavy))
                    VStack(alignment: .leading, spacing: 6) {
                        Text("TOTAL MONTHLY SPEND").font(.system(size: 11, weight: .bold)).tracking(1.4)
                        Text("$142.87").font(.system(size: 40, weight: .heavy))
                        Text("🔥 You could save $38/mo!").font(.system(size: 14))
                    }
                    .padding(22)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .foregroundColor(.white)
                    .background(LinearGradient(colors: [.purple, .blue], startPoint: .topLeading, endPoint: .bottomTrailing))
                    .cornerRadius(26)
                    .shadow(color: .purple.opacity(0.5), radius: 20)
                    HStack(spacing: 13) {
                        StatCard(title: "Active", value: "9")
                        StatCard(title: "Renewing", value: "3")
                        StatCard(title: "Yearly", value: "$1,714")
                    }
                    Text("All Subscriptions").font(.system(size: 19, weight: .bold))
                    ForEach(subs) { sub in
                        HStack(spacing: 12) {
                            Circle().fill(sub.color.opacity(0.25)).frame(width: 42, height: 42)
                                .overlay(Text(sub.emoji).font(.system(size: 20)))
                            VStack(alignment: .leading, spacing: 2) {
                                Text(sub.name).font(.system(size: 16, weight: .semibold))
                                Text("Next: \(sub.next)").font(.system(size: 12)).foregroundColor(.secondary)
                            }
                            Spacer()
                            if sub.soon {
                                Text("Renews Soon!").font(.system(size: 11, weight: .bold))
                                    .padding(.horizontal, 8).padding(.vertical, 4)
                                    .background(Color(red: 1.0, green: 0.2, blue: 0.6)).foregroundColor(.white).cornerRadius(8)
                            }
                            Text(sub.price).font(.system(size: 16, weight: .bold))
                        }
                        .padding(14)
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(18)
                    }
                    Button { } label: {
                        Text("✨ Unlock your savings with Pro").font(.system(size: 16, weight: .bold))
                            .frame(maxWidth: .infinity).padding(16)
                            .background(LinearGradient(colors: [.pink, .orange], startPoint: .leading, endPoint: .trailing))
                            .foregroundColor(.white).cornerRadius(16)
                    }
                }
                .padding(18)
            }
        }
    }
}

struct StatCard: View {
    let title: String; let value: String
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title).font(.system(size: 12)).foregroundColor(.secondary)
            Text(value).font(.system(size: 22, weight: .heavy))
        }
        .padding(15).frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground)).cornerRadius(18)
    }
}
