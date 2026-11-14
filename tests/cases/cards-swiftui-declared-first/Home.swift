import SwiftUI
struct StatCard: View { let v: String; var body: some View { Text(v) } }
struct HomeView: View {
  var body: some View { HStack { StatCard(v: "1"); StatCard(v: "2"); StatCard(v: "3") } }
}
