"""
repo : https://github.com/openmarmot/twe

notes :
A multi-barrel mount that the rest of the game treats as one gun.
The turret holds this object as primary_weapon. Each barrel is a normal
AIGun with its own magazine, cooldown, and projectile spawn.

fire_mode "simultaneous":
    one fire() discharges every barrel that can fire.
    rate_of_fire is the pause between salvos.
    each barrel still will not fire faster than its own rate_of_fire.
    The Drilling uses this. Three guns, one trigger, one salvo per cycle.

fire_mode "sequential":
    one fire() discharges the next barrel that can fire.
    rate_of_fire is the pause between those shots.
    a barrel still will not fire faster than its own rate_of_fire.
    To run every barrel at its own cyclic rate, set the mount
    rate_of_fire to barrel_rate / barrel_count.

The gunner is unchanged. check_if_can_fire() and fire() are the normal
single-gun calls. magazine is the barrel the gunner should judge ammo
type from. reload_weapon() in ai_human sees multi_barrel and fills
every barrel from one reload.
"""

# import built in modules
import copy

# import custom packages
import engine.log
from ai.ai_gun import AIGun


class AIGunMulti(AIGun):
    def __init__(self, owner):
        # set before AIGun.__init__. that assigns magazine and the round
        # counters, and those assignments hit the properties below.
        self.barrels = []
        self.multi_barrel = True
        # "sequential" or "simultaneous"
        self.fire_mode = "sequential"
        self.next_barrel = 0
        self._fire_mode_warned = False
        super().__init__(owner)

    # ---------------------------------------------------------------------------
    @property
    def magazine(self):
        """the barrel magazine the gunner and penetration checks should read.

        A loaded belt is preferred, so the mount is not treated as empty
        while another barrel still has rounds.
        """
        if len(self.barrels) == 0:
            return None
        for barrel in self.barrels:
            mag = barrel.ai.magazine
            if mag is not None and len(mag.ai.projectiles) > 0:
                return mag
        return self.barrels[0].ai.magazine

    # ---------------------------------------------------------------------------
    @magazine.setter
    def magazine(self, new_magazine):
        """put one magazine on the first empty barrel.

        A full reload of every barrel goes through reload_all(). This setter
        only covers a direct assignment.
        """
        if len(self.barrels) == 0:
            return
        for barrel in self.barrels:
            mag = barrel.ai.magazine
            if mag is None or len(mag.ai.projectiles) == 0:
                barrel.ai.magazine = new_magazine
                return
        self.barrels[0].ai.magazine = new_magazine

    # ---------------------------------------------------------------------------
    @property
    def rounds_fired(self):
        total = 0
        for barrel in self.barrels:
            total += barrel.ai.rounds_fired
        return total

    # ---------------------------------------------------------------------------
    @rounds_fired.setter
    def rounds_fired(self, value):
        # AIGun.__init__ assigns 0. the live total is the sum of the barrels.
        pass

    # ---------------------------------------------------------------------------
    @property
    def rounds_hit(self):
        total = 0
        for barrel in self.barrels:
            total += barrel.ai.rounds_hit
        return total

    # ---------------------------------------------------------------------------
    @rounds_hit.setter
    def rounds_hit(self, value):
        pass

    # ---------------------------------------------------------------------------
    def adopt_barrels(self, barrels):
        """take ownership of the barrel guns and copy the gunner-facing stats."""
        self.barrels = list(barrels)
        self.next_barrel = 0
        if len(self.barrels) == 0:
            engine.log.add_data(
                "error", f"ai_gun_multi {self.owner.name} has no barrels", True
            )
            return
        first = self.barrels[0].ai
        self.muzzle_velocity = first.muzzle_velocity
        self.mechanical_accuracy = first.mechanical_accuracy
        self.mechanical_accuracy_deg = first.mechanical_accuracy_deg
        self.range = first.range
        self.indirect_range = first.indirect_range
        self.minimum_range = first.minimum_range
        self.type = first.type
        self.use_antitank = first.use_antitank
        self.use_antipersonnel = first.use_antipersonnel
        self.direct_fire = first.direct_fire
        self.indirect_fire = first.indirect_fire
        self.reload_speed = first.reload_speed

    # ---------------------------------------------------------------------------
    def rounds_loaded(self):
        """rounds currently in all barrels"""
        total = 0
        for barrel in self.barrels:
            mag = barrel.ai.magazine
            if mag is not None:
                total += len(mag.ai.projectiles)
        return total

    # ---------------------------------------------------------------------------
    def check_if_can_fire(self):
        """bool as to whether the mount can fire"""
        if self.damaged or self.action_jammed:
            return False
        if len(self.barrels) == 0:
            return False
        if self._interval_elapsed() is False:
            return False
        if self._mode() == "simultaneous":
            for barrel in self.barrels:
                if barrel.ai.check_if_can_fire():
                    return True
            return False
        return self._next_ready_barrel() is not None

    # ---------------------------------------------------------------------------
    def fire(self):
        """fire one barrel, or every ready barrel, depending on fire_mode"""
        if self.check_if_can_fire() is False:
            return
        fired = False
        if self._mode() == "simultaneous":
            for barrel in self.barrels:
                if barrel.ai.check_if_can_fire():
                    self._prepare_barrel(barrel)
                    barrel.ai.fire()
                    fired = True
        else:
            barrel = self._next_ready_barrel()
            if barrel is not None:
                self._prepare_barrel(barrel)
                barrel.ai.fire()
                fired = True
                index = self.barrels.index(barrel)
                self.next_barrel = (index + 1) % len(self.barrels)
        if fired:
            self.last_fired_time = self.owner.world.world_seconds

    # ---------------------------------------------------------------------------
    def reload_all(self, holder, preferred):
        """load every barrel from the vehicle's stores. return bool.

        preferred is the magazine the gunner or the player picked, or None.
        Every barrel that is empty or holding a different round is filled
        with that projectile type. Belts already of that type are left alone.
        """
        if len(self.barrels) == 0:
            return False
        desired = self._projectile_type(preferred)
        loaded_any = False
        used_preferred = False
        for barrel in self.barrels:
            if self._barrel_keeps_magazine(barrel, desired):
                loaded_any = True
                continue
            if (
                barrel.ai.magazine is not None
                and barrel.ai.magazine.ai.removable is False
            ):
                continue
            choice = None
            if (
                used_preferred is False
                and preferred is not None
                and self._compatible(preferred)
            ):
                choice = preferred
                used_preferred = True
            if choice is None:
                choice = self._pick_stored(holder, desired)
            if choice is None:
                continue
            self._stash(barrel, holder)
            self._take(choice, holder)
            barrel.ai.magazine = choice
            loaded_any = True
        return loaded_any

    # ---------------------------------------------------------------------------
    def _mode(self):
        if self.fire_mode == "simultaneous":
            return "simultaneous"
        if self.fire_mode != "sequential" and self._fire_mode_warned is False:
            self._fire_mode_warned = True
            engine.log.add_data(
                "error",
                f"ai_gun_multi unknown fire_mode {self.fire_mode}",
                True,
            )
        return "sequential"

    # ---------------------------------------------------------------------------
    def _interval_elapsed(self):
        # same comparison as AIGun: a rate of 0 still waits for a new timestamp
        return (
            self.owner.world.world_seconds - self.last_fired_time > self.rate_of_fire
        )

    # ---------------------------------------------------------------------------
    def _next_ready_barrel(self):
        count = len(self.barrels)
        for offset in range(count):
            index = (self.next_barrel + offset) % count
            barrel = self.barrels[index]
            if barrel.ai.check_if_can_fire():
                return barrel
        return None

    # ---------------------------------------------------------------------------
    def _prepare_barrel(self, barrel):
        """copy the mount aim onto one barrel before it fires"""
        barrel.rotation_angle = self.owner.rotation_angle
        barrel.ai.calculated_range = self.calculated_range
        barrel.ai.indirect_fire_mode = self.indirect_fire_mode
        barrel.ai.equipper = self.equipper

    # ---------------------------------------------------------------------------
    def _barrel_keeps_magazine(self, barrel, desired):
        mag = barrel.ai.magazine
        if mag is None or len(mag.ai.projectiles) == 0:
            return False
        if desired is None:
            return True
        return self._projectile_type(mag) == desired

    # ---------------------------------------------------------------------------
    def _projectile_type(self, magazine):
        if magazine is None or len(magazine.ai.projectiles) == 0:
            return None
        return magazine.ai.projectiles[0].ai.projectile_type

    # ---------------------------------------------------------------------------
    def _compatible(self, magazine):
        if magazine is None or magazine.is_gun_magazine is False:
            return False
        if self.owner.world_builder_identity not in magazine.ai.compatible_guns:
            return False
        return len(magazine.ai.projectiles) > 0

    # ---------------------------------------------------------------------------
    def _stored_magazines(self, holder):
        found = []
        containers = [holder.ai.inventory]
        if holder.is_vehicle:
            containers.append(holder.ai.ammo_rack)
        for container in containers:
            for magazine in container:
                if self._compatible(magazine):
                    found.append(magazine)
        return found

    # ---------------------------------------------------------------------------
    def _pick_stored(self, holder, desired):
        best = None
        best_count = -1
        for magazine in self._stored_magazines(holder):
            if desired is not None and self._projectile_type(magazine) != desired:
                continue
            count = len(magazine.ai.projectiles)
            if count > best_count:
                best = magazine
                best_count = count
        return best

    # ---------------------------------------------------------------------------
    def _stash(self, barrel, holder):
        old = barrel.ai.magazine
        if old is None:
            return
        if old.ai.removable is False:
            return
        barrel.ai.magazine = None
        if old.ai.disintegrating and len(old.ai.projectiles) == 0:
            return
        holder.ai.event_add_inventory(old)

    # ---------------------------------------------------------------------------
    def _take(self, magazine, holder):
        if magazine in holder.ai.inventory:
            holder.ai.event_remove_inventory(magazine)
            return
        if holder.is_vehicle and magazine in holder.ai.ammo_rack:
            # event_remove_inventory only removes from the loose inventory.
            # a rack belt has to come off the rack or two barrels can share it.
            holder.ai.ammo_rack.remove(magazine)
            magazine.world_coords = copy.copy(holder.world_coords)
            return
        engine.log.add_data(
            "error",
            "ai_gun_multi.reload_all magazine not in inventory or ammo rack",
            True,
        )
