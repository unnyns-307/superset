/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { useEffect, useState } from 'react';
import { css, styled } from '@apache-superset/core/theme';
import { SupersetClient } from '@superset-ui/core';
import { Icons } from '@superset-ui/core/components/Icons';
import Announcement from 'src/types/Announcement';

const BannerContainer = styled.div<{ severity: string }>`
  ${({ theme, severity }) => css`
    display: flex;
    align-items: center;
    padding: ${theme.sizeUnit * 3}px;
    background-color: ${severity === 'Critical'
      ? theme.colorErrorBg
      : severity === 'Warning'
        ? theme.colorWarningBg
        : severity === 'Success'
          ? theme.colorSuccessBg
          : theme.colorInfoBg};
    border-left: 4px solid
      ${severity === 'Critical'
        ? theme.colorError
        : severity === 'Warning'
          ? theme.colorWarning
          : severity === 'Success'
            ? theme.colorSuccess
            : theme.colorInfo};
    color: ${theme.colorText};
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  `}
`;

const BannerContent = styled.div`
  ${({ theme }) => css`
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: ${theme.sizeUnit}px;
  `}
`;

const BannerTitle = styled.div`
  ${({ theme }) => css`
    font-weight: ${theme.fontWeightStrong};
    font-size: ${theme.fontSize}px;
    display: flex;
    align-items: center;
    gap: ${theme.sizeUnit * 2}px;
  `}
`;

const BannerMessage = styled.div`
  ${({ theme }) => css`
    font-size: ${theme.fontSizeSM}px;
  `}
`;

const MoreBadge = styled.span`
  ${({ theme }) => css`
    background-color: ${theme.colorFillSecondary};
    padding: ${theme.sizeUnit}px ${theme.sizeUnit * 2}px;
    border-radius: ${theme.borderRadius}px;
    font-size: ${theme.fontSizeSM}px;
    font-weight: normal;
  `}
`;

const CloseButton = styled.button`
  ${({ theme }) => css`
    background: none;
    border: none;
    cursor: pointer;
    padding: ${theme.sizeUnit}px;
    color: ${theme.colorTextSecondary};
    display: flex;
    align-items: center;

    &:hover {
      color: ${theme.colorText};
    }
  `}
`;

export default function AnnouncementBanner() {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());

  useEffect(() => {
    // Fetch active announcements
    SupersetClient.get({
      endpoint: '/api/v1/announcement/',
    })
      .then(({ json }) => {
        const activeAnnouncements = (json.result || []).filter(
          (a: Announcement) => a.status === 'Active' && a.show_banner,
        );
        // Sort by severity priority
        const severityOrder = { Critical: 0, Warning: 1, Info: 2, Success: 3 };
        activeAnnouncements.sort(
          (a: Announcement, b: Announcement) =>
            severityOrder[a.severity] - severityOrder[b.severity],
        );
        setAnnouncements(activeAnnouncements);
      })
      .catch(err => {
        console.error('Failed to fetch announcements:', err);
      });
  }, []);

  const handleDismiss = (id: number) => {
    setDismissed(prev => new Set([...prev, id]));
  };

  // Filter out dismissed announcements
  const visibleAnnouncements = announcements.filter(a => !dismissed.has(a.id));

  if (visibleAnnouncements.length === 0) {
    return null;
  }

  // Show the highest priority announcement
  const mainAnnouncement = visibleAnnouncements[0];
  const additionalCount = visibleAnnouncements.length - 1;

  return (
    <BannerContainer severity={mainAnnouncement.severity}>
      <BannerContent>
        <BannerTitle>
          {mainAnnouncement.title}
          {additionalCount > 0 && (
            <MoreBadge>+{additionalCount} more</MoreBadge>
          )}
        </BannerTitle>
        <BannerMessage>{mainAnnouncement.message}</BannerMessage>
      </BannerContent>
      {mainAnnouncement.allow_dismiss && (
        <CloseButton
          onClick={() => handleDismiss(mainAnnouncement.id)}
          aria-label="Dismiss"
        >
          <Icons.CloseOutlined iconSize="l" />
        </CloseButton>
      )}
    </BannerContainer>
  );
}
