package runtime

import (
	rspec "github.com/opencontainers/runtime-spec/specs-go"
	"strings"
)

// ContainerConfig holds runtime configuration
type ContainerConfig struct {
	Args []string
	Env  []string
	Mounts []string // format: host:container
	Network string
}

// GenerateSpec creates a default OCI spec
func GenerateSpec(cfg ContainerConfig) *rspec.Spec {
	rootfs := "rootfs"
	
	// Default Env
	env := []string{
		"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
		"TERM=xterm",
	}
	env = append(env, cfg.Env...)

	// Logic to Handle Network Namespace
	namespaces := []rspec.LinuxNamespace{
		{Type: rspec.PIDNamespace},
		{Type: rspec.IPCNamespace},
		{Type: rspec.UTSNamespace},
		{Type: rspec.MountNamespace},
	}
	
	if cfg.Network != "host" {
		namespaces = append(namespaces, rspec.LinuxNamespace{Type: rspec.NetworkNamespace})
	}

	spec := &rspec.Spec{
		Version: rspec.Version,
		Root: &rspec.Root{
			Path: rootfs,
			Readonly: false,
		},
		Process: &rspec.Process{
			Terminal: false,
			User: rspec.User{
				UID: 0,
				GID: 0,
			},
			Args: cfg.Args,
			Env:  env,
			Cwd:  "/usr/local/searxng",
			Capabilities: &rspec.LinuxCapabilities{
				Bounding: []string{
					"CAP_CHOWN",
					"CAP_DAC_OVERRIDE",
					"CAP_FOWNER",
					"CAP_FSETID",
					"CAP_KILL",
					"CAP_SETGID",
					"CAP_SETUID",
					"CAP_SETPCAP",
					"CAP_LINUX_IMMUTABLE",
					"CAP_NET_BIND_SERVICE",
					"CAP_NET_BROADCAST",
					"CAP_NET_ADMIN",
					"CAP_NET_RAW",
					"CAP_IPC_LOCK",
					"CAP_IPC_OWNER",
					"CAP_SYS_MODULE",
					"CAP_SYS_RAWIO",
					"CAP_SYS_CHROOT",
					"CAP_SYS_PTRACE",
					"CAP_SYS_PACCT",
					"CAP_SYS_ADMIN",
					"CAP_SYS_BOOT",
					"CAP_SYS_NICE",
					"CAP_SYS_RESOURCE",
					"CAP_SYS_TIME",
					"CAP_SYS_TTY_CONFIG",
					"CAP_MKNOD",
					"CAP_LEASE",
					"CAP_AUDIT_WRITE",
					"CAP_AUDIT_CONTROL",
					"CAP_SETFCAP",
					"CAP_MAC_OVERRIDE",
					"CAP_MAC_ADMIN",
					"CAP_SYSLOG",
					"CAP_WAKE_ALARM",
					"CAP_BLOCK_SUSPEND",
					"CAP_AUDIT_READ",
				},
				Effective: []string{
					"CAP_CHOWN",
					"CAP_DAC_OVERRIDE",
					"CAP_FOWNER",
					"CAP_FSETID",
					"CAP_KILL",
					"CAP_SETGID",
					"CAP_SETUID",
					"CAP_SETPCAP",
					"CAP_LINUX_IMMUTABLE",
					"CAP_NET_BIND_SERVICE",
					"CAP_NET_BROADCAST",
					"CAP_NET_ADMIN",
					"CAP_NET_RAW",
					"CAP_IPC_LOCK",
					"CAP_IPC_OWNER",
					"CAP_SYS_MODULE",
					"CAP_SYS_RAWIO",
					"CAP_SYS_CHROOT",
					"CAP_SYS_PTRACE",
					"CAP_SYS_PACCT",
					"CAP_SYS_ADMIN",
					"CAP_SYS_BOOT",
					"CAP_SYS_NICE",
					"CAP_SYS_RESOURCE",
					"CAP_SYS_TIME",
					"CAP_SYS_TTY_CONFIG",
					"CAP_MKNOD",
					"CAP_LEASE",
					"CAP_AUDIT_WRITE",
					"CAP_AUDIT_CONTROL",
					"CAP_SETFCAP",
					"CAP_MAC_OVERRIDE",
					"CAP_MAC_ADMIN",
					"CAP_SYSLOG",
					"CAP_WAKE_ALARM",
					"CAP_BLOCK_SUSPEND",
					"CAP_AUDIT_READ",
				},
				Inheritable: []string{
					"CAP_CHOWN",
					"CAP_DAC_OVERRIDE",
					"CAP_FOWNER",
					"CAP_FSETID",
					"CAP_KILL",
					"CAP_SETGID",
					"CAP_SETUID",
					"CAP_SETPCAP",
					"CAP_LINUX_IMMUTABLE",
					"CAP_NET_BIND_SERVICE",
					"CAP_NET_BROADCAST",
					"CAP_NET_ADMIN",
					"CAP_NET_RAW",
					"CAP_IPC_LOCK",
					"CAP_IPC_OWNER",
					"CAP_SYS_MODULE",
					"CAP_SYS_RAWIO",
					"CAP_SYS_CHROOT",
					"CAP_SYS_PTRACE",
					"CAP_SYS_PACCT",
					"CAP_SYS_ADMIN",
					"CAP_SYS_BOOT",
					"CAP_SYS_NICE",
					"CAP_SYS_RESOURCE",
					"CAP_SYS_TIME",
					"CAP_SYS_TTY_CONFIG",
					"CAP_MKNOD",
					"CAP_LEASE",
					"CAP_AUDIT_WRITE",
					"CAP_AUDIT_CONTROL",
					"CAP_SETFCAP",
					"CAP_MAC_OVERRIDE",
					"CAP_MAC_ADMIN",
					"CAP_SYSLOG",
					"CAP_WAKE_ALARM",
					"CAP_BLOCK_SUSPEND",
					"CAP_AUDIT_READ",
				},
				Permitted: []string{
					"CAP_CHOWN",
					"CAP_DAC_OVERRIDE",
					"CAP_FOWNER",
					"CAP_FSETID",
					"CAP_KILL",
					"CAP_SETGID",
					"CAP_SETUID",
					"CAP_SETPCAP",
					"CAP_LINUX_IMMUTABLE",
					"CAP_NET_BIND_SERVICE",
					"CAP_NET_BROADCAST",
					"CAP_NET_ADMIN",
					"CAP_NET_RAW",
					"CAP_IPC_LOCK",
					"CAP_IPC_OWNER",
					"CAP_SYS_MODULE",
					"CAP_SYS_RAWIO",
					"CAP_SYS_CHROOT",
					"CAP_SYS_PTRACE",
					"CAP_SYS_PACCT",
					"CAP_SYS_ADMIN",
					"CAP_SYS_BOOT",
					"CAP_SYS_NICE",
					"CAP_SYS_RESOURCE",
					"CAP_SYS_TIME",
					"CAP_SYS_TTY_CONFIG",
					"CAP_MKNOD",
					"CAP_LEASE",
					"CAP_AUDIT_WRITE",
					"CAP_AUDIT_CONTROL",
					"CAP_SETFCAP",
					"CAP_MAC_OVERRIDE",
					"CAP_MAC_ADMIN",
					"CAP_SYSLOG",
					"CAP_WAKE_ALARM",
					"CAP_BLOCK_SUSPEND",
					"CAP_AUDIT_READ",
				},
				Ambient: []string{
					"CAP_CHOWN",
					"CAP_DAC_OVERRIDE",
					"CAP_FOWNER",
					"CAP_FSETID",
					"CAP_KILL",
					"CAP_SETGID",
					"CAP_SETUID",
					"CAP_SETPCAP",
					"CAP_LINUX_IMMUTABLE",
					"CAP_NET_BIND_SERVICE",
					"CAP_NET_BROADCAST",
					"CAP_NET_ADMIN",
					"CAP_NET_RAW",
					"CAP_IPC_LOCK",
					"CAP_IPC_OWNER",
					"CAP_SYS_MODULE",
					"CAP_SYS_RAWIO",
					"CAP_SYS_CHROOT",
					"CAP_SYS_PTRACE",
					"CAP_SYS_PACCT",
					"CAP_SYS_ADMIN",
					"CAP_SYS_BOOT",
					"CAP_SYS_NICE",
					"CAP_SYS_RESOURCE",
					"CAP_SYS_TIME",
					"CAP_SYS_TTY_CONFIG",
					"CAP_MKNOD",
					"CAP_LEASE",
					"CAP_AUDIT_WRITE",
					"CAP_AUDIT_CONTROL",
					"CAP_SETFCAP",
					"CAP_MAC_OVERRIDE",
					"CAP_MAC_ADMIN",
					"CAP_SYSLOG",
					"CAP_WAKE_ALARM",
					"CAP_BLOCK_SUSPEND",
					"CAP_AUDIT_READ",
				},
			},
		},
		Hostname: "lite-dock",
		Mounts: []rspec.Mount{
			{
				Destination: "/proc",
				Type:        "proc",
				Source:      "proc",
			},
			{
				Destination: "/etc/resolv.conf",
				Type:        "bind",
				Source:      "/etc/resolv.conf",
				Options:     []string{"bind", "ro"},
			},
			{
				Destination: "/dev",
				Type:        "tmpfs",
				Source:      "tmpfs",
				Options:     []string{"nosuid", "strictatime", "mode=755", "size=65536k"},
			},
			{
				Destination: "/dev/pts",
				Type:        "devpts",
				Source:      "devpts",
				Options:     []string{"nosuid", "noexec", "newinstance", "ptmxmode=0666", "mode=0620", "gid=5"},
			},
			{
				Destination: "/sys",
				Type:        "sysfs",
				Source:      "sysfs",
				Options:     []string{"nosuid", "noexec", "nodev", "ro"},
			},
		},
		Linux: &rspec.Linux{
			Namespaces: namespaces,
		},
	}
	
	// Process custom mounts
	for _, m := range cfg.Mounts {
		// format host:container
		parts := strings.Split(m, ":")
		if len(parts) == 2 {
			spec.Mounts = append(spec.Mounts, rspec.Mount{
				Destination: parts[1],
				Source:      parts[0],
				Type:        "bind",
				Options:     []string{"rbind", "rw"},
			})
		}
	}
	
	return spec
}
