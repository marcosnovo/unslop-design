Text("Plan").foregroundStyle(.white.opacity(0.6)).shadow(radius: 12)
Button { } label: { Text("Upgrade") }
Button { model.upgrade() } label: { Text("Upgrade") }
