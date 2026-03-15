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

import { useMemo, useState } from 'react';
import rison from 'rison';
import { t } from '@apache-superset/core/translation';
import { SupersetClient } from '@superset-ui/core';
import { useListViewResource } from 'src/views/CRUD/hooks';
import { createFetchRelated, createErrorHandler } from 'src/views/CRUD/utils';
import withToasts from 'src/components/MessageToasts/withToasts';
import SubMenu, { SubMenuProps } from 'src/features/home/SubMenu';
import { DeleteModal, ConfirmStatusChange } from '@superset-ui/core/components';
import {
  ModifiedInfo,
  ListView,
  ListViewFilterOperator as FilterOperator,
  ListViewActionsBar,
  type ListViewActionProps,
  type ListViewProps,
  type ListViewFilters,
} from 'src/components';
import { WIDER_DROPDOWN_WIDTH } from 'src/components/ListView/utils';
import Announcement from 'src/types/Announcement';
import { QueryObjectColumns } from 'src/views/CRUD/types';

const PAGE_SIZE = 25;

interface AnnouncementListProps {
  addDangerToast: (msg: string) => void;
  addSuccessToast: (msg: string) => void;
  user: {
    userId: string | number;
    firstName: string;
    lastName: string;
  };
}

function AnnouncementList({
  addDangerToast,
  addSuccessToast,
  user,
}: AnnouncementListProps) {
  const {
    state: {
      loading,
      resourceCount: announcementsCount,
      resourceCollection: announcements,
      bulkSelectEnabled,
    },
    hasPerm,
    fetchData,
    refreshData,
    toggleBulkSelect,
  } = useListViewResource<Announcement>(
    'announcement',
    t('Announcements'),
    addDangerToast,
  );

  const [announcementCurrentlyDeleting, setAnnouncementCurrentlyDeleting] =
    useState<Announcement | null>(null);

  const handleAnnouncementDelete = ({ id, title }: Announcement) => {
    SupersetClient.delete({
      endpoint: `/api/v1/announcement/${id}`,
    }).then(
      () => {
        refreshData();
        setAnnouncementCurrentlyDeleting(null);
        addSuccessToast(t('Deleted: %s', title));
      },
      createErrorHandler(errMsg =>
        addDangerToast(t('There was an issue deleting %s: %s', title, errMsg)),
      ),
    );
  };

  const handleBulkAnnouncementDelete = (
    announcementsToDelete: Announcement[],
  ) => {
    SupersetClient.delete({
      endpoint: `/api/v1/announcement/?q=${rison.encode(
        announcementsToDelete.map(({ id }) => id),
      )}`,
    }).then(
      ({ json = {} }) => {
        refreshData();
        addSuccessToast(json.message);
      },
      createErrorHandler(errMsg =>
        addDangerToast(
          t('There was an issue deleting the selected announcements: %s', errMsg),
        ),
      ),
    );
  };

  const canCreate = hasPerm('can_write');
  const canEdit = hasPerm('can_write');
  const canDelete = hasPerm('can_write');

  const initialSort = [{ id: 'changed_on', desc: true }];

  const columns = useMemo(
    () => [
      {
        accessor: 'title',
        Header: t('Title'),
        size: 'xl',
      },
      {
        accessor: 'severity',
        Header: t('Severity'),
        size: 'md',
        Cell: ({ value }: any) => {
          const colors: Record<string, string> = {
            Critical: '#ff4d4f',
            Warning: '#faad14',
            Info: '#1890ff',
            Success: '#52c41a',
          };
          return (
            <span style={{ color: colors[value] || '#000', fontWeight: 'bold' }}>
              {value}
            </span>
          );
        },
      },
      {
        accessor: 'category',
        Header: t('Category'),
        size: 'md',
      },
      {
        accessor: 'status',
        Header: t('Status'),
        size: 'md',
      },
      {
        accessor: 'start_dttm',
        Header: t('Start Date'),
        size: 'lg',
        Cell: ({ value }: any) =>
          value ? new Date(value).toLocaleString() : '',
      },
      {
        accessor: 'end_dttm',
        Header: t('End Date'),
        size: 'lg',
        Cell: ({ value }: any) =>
          value ? new Date(value).toLocaleString() : '',
      },
      {
        Cell: ({
          row: {
            original: {
              changed_on_delta_humanized: changedOn,
              changed_by: changedBy,
            },
          },
        }: any) => <ModifiedInfo date={changedOn} user={changedBy} />,
        Header: t('Last modified'),
        accessor: 'changed_on',
        size: 'xl',
      },
      {
        Cell: ({ row: { original } }: any) => {
          const handleDelete = () => setAnnouncementCurrentlyDeleting(original);

          const actions = [
            canDelete
              ? {
                  label: 'delete-action',
                  tooltip: t('Delete announcement'),
                  placement: 'bottom',
                  icon: 'DeleteOutlined',
                  onClick: handleDelete,
                }
              : null,
          ].filter(item => !!item);

          return (
            <ListViewActionsBar actions={actions as ListViewActionProps[]} />
          );
        },
        Header: t('Actions'),
        id: 'actions',
        disableSortBy: true,
        hidden: !canEdit && !canDelete,
        size: 'xl',
      },
      {
        accessor: QueryObjectColumns.ChangedBy,
        hidden: true,
      },
    ],
    [canDelete, canCreate],
  );

  const subMenuButtons: SubMenuProps['buttons'] = [];

  if (canDelete) {
    subMenuButtons.push({
      name: t('Bulk select'),
      onClick: toggleBulkSelect,
      buttonStyle: 'secondary',
    });
  }

  const filters: ListViewFilters = useMemo(
    () => [
      {
        Header: t('Title'),
        key: 'search',
        id: 'title',
        input: 'search',
        operator: FilterOperator.Contains,
      },
      {
        Header: t('Severity'),
        key: 'severity',
        id: 'severity',
        input: 'select',
        operator: FilterOperator.Equals,
        unfilteredLabel: t('All'),
        selects: [
          { label: 'Critical', value: 'Critical' },
          { label: 'Warning', value: 'Warning' },
          { label: 'Info', value: 'Info' },
          { label: 'Success', value: 'Success' },
        ],
      },
      {
        Header: t('Status'),
        key: 'status',
        id: 'status',
        input: 'select',
        operator: FilterOperator.Equals,
        unfilteredLabel: t('All'),
        selects: [
          { label: 'Draft', value: 'Draft' },
          { label: 'Scheduled', value: 'Scheduled' },
          { label: 'Active', value: 'Active' },
          { label: 'Expired', value: 'Expired' },
        ],
      },
      {
        Header: t('Changed by'),
        key: 'changed_by',
        id: 'changed_by',
        input: 'select',
        operator: FilterOperator.RelationOneMany,
        unfilteredLabel: t('All'),
        fetchSelects: createFetchRelated(
          'announcement',
          'changed_by',
          createErrorHandler(errMsg =>
            t('An error occurred while fetching changed by values: %s', errMsg),
          ),
          user,
        ),
        paginate: true,
        dropdownStyle: { minWidth: WIDER_DROPDOWN_WIDTH },
      },
    ],
    [],
  );

  const emptyState = {
    title: t('No announcements yet'),
    image: 'filter-results.svg',
  };

  return (
    <>
      <SubMenu name={t('Announcements')} buttons={subMenuButtons} />
      {announcementCurrentlyDeleting && (
        <DeleteModal
          description={t(
            'This action will permanently delete the announcement.',
          )}
          onConfirm={() => {
            if (announcementCurrentlyDeleting) {
              handleAnnouncementDelete(announcementCurrentlyDeleting);
            }
          }}
          onHide={() => setAnnouncementCurrentlyDeleting(null)}
          open
          title={t('Delete Announcement?')}
        />
      )}
      <ConfirmStatusChange
        title={t('Please confirm')}
        description={t(
          'Are you sure you want to delete the selected announcements?',
        )}
        onConfirm={handleBulkAnnouncementDelete}
      >
        {confirmDelete => {
          const bulkActions: ListViewProps['bulkActions'] = canDelete
            ? [
                {
                  key: 'delete',
                  name: t('Delete'),
                  onSelect: confirmDelete,
                  type: 'danger',
                },
              ]
            : [];

          return (
            <ListView<Announcement>
              className="announcements-list-view"
              columns={columns}
              count={announcementsCount}
              data={announcements}
              fetchData={fetchData}
              filters={filters}
              initialSort={initialSort}
              loading={loading}
              pageSize={PAGE_SIZE}
              bulkActions={bulkActions}
              bulkSelectEnabled={bulkSelectEnabled}
              disableBulkSelect={toggleBulkSelect}
              addDangerToast={addDangerToast}
              addSuccessToast={addSuccessToast}
              emptyState={emptyState}
              refreshData={refreshData}
            />
          );
        }}
      </ConfirmStatusChange>
    </>
  );
}

export default withToasts(AnnouncementList);
