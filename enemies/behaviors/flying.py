class FlyingBehavior:
    def update(self, player, tiles):
        e = self.owner
        e.state = "idle"

        e.rect.x += e.speed if player.rect.centerx > e.rect.centerx else -e.speed
        e.rect.y += e.speed if player.rect.centery > e.rect.centery else -e.speed
