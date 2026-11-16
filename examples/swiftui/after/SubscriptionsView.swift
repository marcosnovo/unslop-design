import SwiftUI

struct SubscriptionsView: View {
    let subs = Subscription.samples.sorted { $0.nextDate < $1.nextDate }
    var body: some View {
        NavigationStack {
            List {
                Section {
                    VStack(alignment: .leading, spacing: Space.s1) {
                        Text("Per month").font(TypeScale.meta).foregroundStyle(Ink.secondary)
                        AmountText(Subscription.monthlyTotal(subs)).font(TypeScale.hero)
                        Text("\(subs.count) active · \(Subscription.yearlyTotal(subs).formatted(.currency(code: "USD"))) a year")
                            .font(TypeScale.meta).foregroundStyle(Ink.secondary)
                    }
                    .listRowBackground(Color.clear)
                    .listRowInsets(EdgeInsets(top: Space.s2, leading: Space.s4, bottom: Space.s6, trailing: Space.s4))
                }
                Section("Next charges") {
                    ForEach(subs) { sub in
                        SubscriptionRow(sub: sub)
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("Subscriptions")
        }
    }
}

struct SubscriptionRow: View {
    let sub: Subscription
    var body: some View {
        HStack(spacing: Space.s3) {
            Monogram(name: sub.name).frame(width: Size.monogram, height: Size.monogram)
            VStack(alignment: .leading, spacing: Space.s1 / 2) {
                Text(sub.name).font(TypeScale.body).lineLimit(2)
                Text(sub.nextLabel).font(TypeScale.meta)
                    .foregroundStyle(sub.isSoon ? Ink.soon : Ink.secondary)
            }
            Spacer(minLength: Space.s2)
            AmountText(sub.price).font(TypeScale.body)
        }
        .accessibilityElement(children: .combine)
    }
}
